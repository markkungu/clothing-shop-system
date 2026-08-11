<script setup>

import { ref, reactive, onMounted } from "vue"

import productService from "../api/productService"
import variantService from "../api/variantService"


const products = ref([])
const loading = ref(false)
const errorMsg = ref("")
const showArchived = ref(false)


// --- Add-style form ---------------------------------------------------------
const emptyStyle = () => ({ name: "", brand: "", category: "", description: "" })
const styleForm = reactive(emptyStyle())
const savingStyle = ref(false)


// --- Per-style add-variant forms (keyed by product id) ----------------------
const variantForms = reactive({})
const emptyVariant = () => ({
    size: "", color: "", sku: "", price: "", cost_price: "",
    stock_quantity: 0, reorder_level: 5
})
const ensureVariantForm = (id) => {
    if (!variantForms[id]) variantForms[id] = emptyVariant()
}


// --- Edit state -------------------------------------------------------------
const editingStyleId = ref(null)
const styleEdit = reactive({ name: "", brand: "", category: "", description: "" })

const editingVariantId = ref(null)
const variantEdit = reactive({ price: 0, cost_price: 0, stock_quantity: 0, reorder_level: 0 })


// --- Load -------------------------------------------------------------------
const loadProducts = async () => {
    try {
        loading.value = true
        products.value = await productService.getProducts(showArchived.value)
        products.value.forEach(p => ensureVariantForm(p.id))
    } catch (error) {
        console.log(error)
        errorMsg.value = "Could not load products from the backend."
    } finally {
        loading.value = false
    }
}


// --- Style: add / archive / restore / edit ----------------------------------
const addStyle = async () => {
    errorMsg.value = ""
    if (!styleForm.name) { errorMsg.value = "Style name is required."; return }
    try {
        savingStyle.value = true
        await productService.createProduct({
            name: styleForm.name,
            brand: styleForm.brand || null,
            category: styleForm.category || null,
            description: styleForm.description || null,
            variants: []
        })
        Object.assign(styleForm, emptyStyle())
        await loadProducts()
    } catch (error) {
        console.log(error)
        errorMsg.value = "Failed to add style."
    } finally {
        savingStyle.value = false
    }
}

const archiveStyle = async (id) => {
    errorMsg.value = ""
    try { await productService.archiveProduct(id); await loadProducts() }
    catch (e) { console.log(e); errorMsg.value = "Failed to archive style." }
}

const restoreStyle = async (id) => {
    errorMsg.value = ""
    try { await productService.updateProduct(id, { is_active: true }); await loadProducts() }
    catch (e) { console.log(e); errorMsg.value = "Failed to restore style." }
}

const startEditStyle = (p) => {
    editingStyleId.value = p.id
    Object.assign(styleEdit, {
        name: p.name, brand: p.brand || "", category: p.category || "", description: p.description || ""
    })
}
const cancelEditStyle = () => { editingStyleId.value = null }
const saveStyle = async (id) => {
    errorMsg.value = ""
    try {
        await productService.updateProduct(id, {
            name: styleEdit.name,
            brand: styleEdit.brand || null,
            category: styleEdit.category || null,
            description: styleEdit.description || null
        })
        editingStyleId.value = null
        await loadProducts()
    } catch (e) { console.log(e); errorMsg.value = "Failed to save style." }
}


// --- Variant: add / edit(restock) / archive ---------------------------------
const suggestSku = (product, form) => {
    const base = (product.brand || product.name || "SKU").replace(/[^a-zA-Z0-9]/g, "").slice(0, 4).toUpperCase()
    const color = (form.color || "").replace(/[^a-zA-Z0-9]/g, "").slice(0, 3).toUpperCase()
    const size = (form.size || "").replace(/[^a-zA-Z0-9]/g, "").toUpperCase()
    return [base, color, size].filter(Boolean).join("-")
}

const addVariant = async (product) => {
    errorMsg.value = ""
    const form = variantForms[product.id]
    if (form.price === "") { errorMsg.value = "Variant price is required."; return }
    try {
        await variantService.addVariant(product.id, {
            sku: form.sku || suggestSku(product, form),
            size: form.size || null,
            color: form.color || null,
            price: Number(form.price),
            cost_price: form.cost_price === "" ? null : Number(form.cost_price),
            stock_quantity: Number(form.stock_quantity),
            reorder_level: Number(form.reorder_level)
        })
        variantForms[product.id] = emptyVariant()
        await loadProducts()
    } catch (error) {
        console.log(error)
        errorMsg.value = error?.response?.data?.detail || "Failed to add variant."
    }
}

const startEditVariant = (v) => {
    editingVariantId.value = v.id
    Object.assign(variantEdit, {
        price: Number(v.price),
        cost_price: v.cost_price === null ? "" : Number(v.cost_price),
        stock_quantity: v.stock_quantity,
        reorder_level: v.reorder_level
    })
}
const cancelEditVariant = () => { editingVariantId.value = null }
const saveVariant = async (id) => {
    errorMsg.value = ""
    try {
        await variantService.updateVariant(id, {
            price: Number(variantEdit.price),
            cost_price: variantEdit.cost_price === "" ? null : Number(variantEdit.cost_price),
            stock_quantity: Number(variantEdit.stock_quantity),
            reorder_level: Number(variantEdit.reorder_level)
        })
        editingVariantId.value = null
        await loadProducts()
    } catch (e) {
        console.log(e)
        errorMsg.value = e?.response?.data?.detail || "Failed to save variant."
    }
}

// Quick restock: add N units to current stock
const restock = async (v, amount) => {
    errorMsg.value = ""
    try {
        await variantService.updateVariant(v.id, { stock_quantity: v.stock_quantity + amount })
        await loadProducts()
    } catch (e) { console.log(e); errorMsg.value = "Failed to restock." }
}

const archiveVariant = async (variantId) => {
    errorMsg.value = ""
    try { await variantService.archiveVariant(variantId); await loadProducts() }
    catch (e) { console.log(e); errorMsg.value = "Failed to delete variant." }
}


const totalStock = (product) =>
    product.variants.reduce((sum, v) => sum + (v.stock_quantity || 0), 0)
const isLow = (v) => v.stock_quantity <= v.reorder_level


onMounted(loadProducts)

</script>



<template>
<div class="p-6 max-w-6xl mx-auto">

    <div class="flex items-center justify-between mb-6">
        <h1 class="text-3xl font-bold">Inventory</h1>
        <label class="flex items-center gap-2 text-sm text-gray-600">
            <input type="checkbox" v-model="showArchived" @change="loadProducts" />
            Show archived
        </label>
    </div>

    <p v-if="errorMsg" class="mb-4 rounded-lg bg-red-100 text-red-700 px-4 py-2">{{ errorMsg }}</p>


    <!-- Add a new style -->
    <form @submit.prevent="addStyle"
        class="bg-white rounded-xl shadow p-5 mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <input v-model="styleForm.name" placeholder="Style name *" class="border rounded px-3 py-2" />
        <input v-model="styleForm.brand" placeholder="Brand" class="border rounded px-3 py-2" />
        <input v-model="styleForm.category" placeholder="Category" class="border rounded px-3 py-2" />
        <input v-model="styleForm.description" placeholder="Description" class="border rounded px-3 py-2" />
        <button type="submit" :disabled="savingStyle"
            class="md:col-span-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded px-4 py-2">
            {{ savingStyle ? "Adding..." : "Add Style" }}
        </button>
    </form>


    <div v-if="loading" class="text-gray-500">Loading products...</div>
    <div v-else-if="products.length === 0" class="text-gray-500">No products yet. Add a style above.</div>


    <!-- Styles -->
    <div v-else class="space-y-6">

        <div v-for="product in products" :key="product.id"
            class="bg-white rounded-xl shadow p-5" :class="{ 'opacity-60': !product.is_active }">

            <!-- Header: view or edit -->
            <div v-if="editingStyleId !== product.id" class="flex items-start justify-between mb-3">
                <div>
                    <h2 class="font-bold text-xl">
                        {{ product.name }}
                        <span v-if="!product.is_active"
                            class="ml-2 text-xs bg-gray-300 text-gray-700 rounded px-2 py-0.5 align-middle">Archived</span>
                    </h2>
                    <p class="text-gray-500 text-sm">
                        {{ product.brand || "—" }} · {{ product.category || "Uncategorised" }}
                        · Total stock: <span class="font-semibold">{{ totalStock(product) }}</span>
                    </p>
                </div>
                <div class="flex gap-2">
                    <button @click="startEditStyle(product)"
                        class="text-sm bg-gray-100 hover:bg-gray-200 rounded px-3 py-1">Edit</button>
                    <button v-if="product.is_active" @click="archiveStyle(product.id)"
                        class="text-sm bg-gray-200 hover:bg-gray-300 rounded px-3 py-1">Archive</button>
                    <button v-else @click="restoreStyle(product.id)"
                        class="text-sm bg-green-600 hover:bg-green-700 text-white rounded px-3 py-1">Restore</button>
                </div>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-4 gap-2 mb-3">
                <input v-model="styleEdit.name" placeholder="Name" class="border rounded px-2 py-1" />
                <input v-model="styleEdit.brand" placeholder="Brand" class="border rounded px-2 py-1" />
                <input v-model="styleEdit.category" placeholder="Category" class="border rounded px-2 py-1" />
                <input v-model="styleEdit.description" placeholder="Description" class="border rounded px-2 py-1" />
                <div class="md:col-span-4 flex gap-2">
                    <button @click="saveStyle(product.id)"
                        class="text-sm bg-blue-600 hover:bg-blue-700 text-white rounded px-3 py-1">Save</button>
                    <button @click="cancelEditStyle"
                        class="text-sm bg-gray-200 hover:bg-gray-300 rounded px-3 py-1">Cancel</button>
                </div>
            </div>


            <!-- Variants table -->
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="text-left text-gray-500 border-b">
                            <th class="py-1 pr-3">SKU</th>
                            <th class="py-1 pr-3">Size</th>
                            <th class="py-1 pr-3">Color</th>
                            <th class="py-1 pr-3">Price</th>
                            <th class="py-1 pr-3">Stock</th>
                            <th class="py-1 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="v in product.variants" :key="v.id" class="border-b last:border-0 align-middle">

                            <!-- Non-edit row -->
                            <template v-if="editingVariantId !== v.id">
                                <td class="py-1 pr-3 font-mono">{{ v.sku }}</td>
                                <td class="py-1 pr-3">{{ v.size || "—" }}</td>
                                <td class="py-1 pr-3">{{ v.color || "—" }}</td>
                                <td class="py-1 pr-3">Ksh {{ v.price }}</td>
                                <td class="py-1 pr-3">
                                    <span :class="isLow(v) ? 'text-red-600 font-semibold' : ''">
                                        {{ v.stock_quantity }}
                                        <span v-if="isLow(v)" title="At or below reorder level">⚠</span>
                                    </span>
                                </td>
                                <td class="py-1 text-right whitespace-nowrap">
                                    <button @click="restock(v, 10)"
                                        class="text-green-700 hover:text-green-900 text-xs mr-2" title="Add 10 to stock">+10</button>
                                    <button @click="startEditVariant(v)"
                                        class="text-blue-600 hover:text-blue-800 text-xs mr-2">Edit</button>
                                    <button @click="archiveVariant(v.id)"
                                        class="text-red-600 hover:text-red-800 text-xs">Delete</button>
                                </td>
                            </template>

                            <!-- Edit row -->
                            <template v-else>
                                <td class="py-1 pr-3 font-mono">{{ v.sku }}</td>
                                <td class="py-1 pr-3">{{ v.size || "—" }}</td>
                                <td class="py-1 pr-3">{{ v.color || "—" }}</td>
                                <td class="py-1 pr-3">
                                    <input v-model="variantEdit.price" type="number" step="0.01"
                                        class="border rounded w-20 px-1 py-0.5" />
                                </td>
                                <td class="py-1 pr-3">
                                    <input v-model="variantEdit.stock_quantity" type="number"
                                        class="border rounded w-16 px-1 py-0.5" />
                                </td>
                                <td class="py-1 text-right whitespace-nowrap">
                                    <span class="text-xs text-gray-500 mr-2">reorder
                                        <input v-model="variantEdit.reorder_level" type="number"
                                            class="border rounded w-12 px-1 py-0.5" /></span>
                                    <button @click="saveVariant(v.id)"
                                        class="text-blue-600 hover:text-blue-800 text-xs mr-2">Save</button>
                                    <button @click="cancelEditVariant"
                                        class="text-gray-500 hover:text-gray-700 text-xs">Cancel</button>
                                </td>
                            </template>

                        </tr>
                        <tr v-if="product.variants.length === 0">
                            <td colspan="6" class="py-2 text-gray-400 italic">No sizes/colors yet — add one below.</td>
                        </tr>
                    </tbody>
                </table>
            </div>


            <!-- Add variant to this style -->
            <div v-if="product.is_active && variantForms[product.id]"
                class="mt-3 grid grid-cols-2 md:grid-cols-7 gap-2 items-center">
                <input v-model="variantForms[product.id].size" placeholder="Size" class="border rounded px-2 py-1 text-sm" />
                <input v-model="variantForms[product.id].color" placeholder="Color" class="border rounded px-2 py-1 text-sm" />
                <input v-model="variantForms[product.id].sku"
                    :placeholder="suggestSku(product, variantForms[product.id]) || 'SKU (auto)'"
                    class="border rounded px-2 py-1 text-sm font-mono" />
                <input v-model="variantForms[product.id].price" type="number" step="0.01" placeholder="Price *" class="border rounded px-2 py-1 text-sm" />
                <input v-model="variantForms[product.id].cost_price" type="number" step="0.01" placeholder="Cost" class="border rounded px-2 py-1 text-sm" />
                <input v-model="variantForms[product.id].stock_quantity" type="number" placeholder="Qty" class="border rounded px-2 py-1 text-sm" />
                <button @click="addVariant(product)"
                    class="bg-blue-600 hover:bg-blue-700 text-white rounded px-3 py-1 text-sm">Add size</button>
            </div>

        </div>

    </div>

</div>
</template>
