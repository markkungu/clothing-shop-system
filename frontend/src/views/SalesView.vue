<script setup>

import { ref, computed, onMounted } from "vue"

import productService from "../api/productService"
import saleService from "../api/saleService"


const products = ref([])
const loading = ref(false)
const errorMsg = ref("")
const search = ref("")

const cart = ref([])          // { variant_id, label, sku, price, stock, quantity }
const paymentMethod = ref("cash")
const customerName = ref("")
const submitting = ref(false)
const lastReceipt = ref(null)


// Flatten active variants (with stock) into a sellable list
const sellable = computed(() => {
    const rows = []
    for (const p of products.value) {
        for (const v of p.variants) {
            if (!v.is_active) continue
            rows.push({
                variant_id: v.id,
                sku: v.sku,
                label: `${p.name} — ${v.size || ""} ${v.color || ""}`.trim(),
                price: Number(v.price),
                stock: v.stock_quantity
            })
        }
    }
    const q = search.value.trim().toLowerCase()
    if (!q) return rows
    return rows.filter(r =>
        r.label.toLowerCase().includes(q) || r.sku.toLowerCase().includes(q)
    )
})


const loadProducts = async () => {
    try {
        loading.value = true
        products.value = await productService.getProducts(false)
    } catch (e) {
        console.log(e)
        errorMsg.value = "Could not load products."
    } finally {
        loading.value = false
    }
}


const inCart = (variantId) => cart.value.find(c => c.variant_id === variantId)

const addToCart = (row) => {
    errorMsg.value = ""
    if (row.stock <= 0) { errorMsg.value = `${row.sku} is out of stock.`; return }
    const existing = inCart(row.variant_id)
    if (existing) {
        if (existing.quantity < row.stock) existing.quantity++
        else errorMsg.value = `Only ${row.stock} of ${row.sku} in stock.`
    } else {
        cart.value.push({ ...row, quantity: 1 })
    }
}

const removeLine = (variantId) => {
    cart.value = cart.value.filter(c => c.variant_id !== variantId)
}

const clampQty = (line) => {
    if (line.quantity < 1) line.quantity = 1
    if (line.quantity > line.stock) line.quantity = line.stock
}

const cartTotal = computed(() =>
    cart.value.reduce((sum, l) => sum + l.price * l.quantity, 0)
)


const completeSale = async () => {
    errorMsg.value = ""
    if (cart.value.length === 0) { errorMsg.value = "Cart is empty."; return }

    try {
        submitting.value = true
        const sale = await saleService.createSale({
            payment_method: paymentMethod.value,
            customer_name: customerName.value || null,
            items: cart.value.map(l => ({
                variant_id: l.variant_id,
                quantity: Number(l.quantity)
            }))
        })
        lastReceipt.value = sale
        cart.value = []
        customerName.value = ""
        await loadProducts()   // refresh stock levels
    } catch (e) {
        console.log(e)
        errorMsg.value = e?.response?.data?.detail || "Failed to complete sale."
    } finally {
        submitting.value = false
    }
}


onMounted(loadProducts)

</script>



<template>
<div class="p-6 max-w-6xl mx-auto">

    <h1 class="text-3xl font-bold mb-6">Sell</h1>

    <p v-if="errorMsg" class="mb-4 rounded-lg bg-red-100 text-red-700 px-4 py-2">
        {{ errorMsg }}
    </p>

    <!-- Receipt confirmation -->
    <div v-if="lastReceipt"
        class="mb-6 rounded-lg bg-green-50 border border-green-300 p-4">
        <div class="flex justify-between items-center">
            <span class="font-semibold text-green-800">
                ✅ Sale #{{ lastReceipt.id }} recorded — Ksh {{ lastReceipt.total_amount }}
            </span>
            <button @click="lastReceipt = null" class="text-green-700 text-sm">dismiss</button>
        </div>
        <ul class="text-sm text-green-900 mt-2 list-disc ml-5">
            <li v-for="i in lastReceipt.items" :key="i.id">
                {{ i.quantity }} × {{ i.sku }} @ Ksh {{ i.unit_price }} = Ksh {{ i.line_total }}
            </li>
        </ul>
    </div>


    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Product picker -->
        <div class="lg:col-span-2 bg-white rounded-xl shadow p-5">
            <input v-model="search" placeholder="Search by name or SKU..."
                class="border rounded px-3 py-2 w-full mb-3" />

            <div v-if="loading" class="text-gray-500">Loading...</div>
            <div v-else-if="sellable.length === 0" class="text-gray-400 italic">No items found.</div>

            <div v-else class="overflow-x-auto max-h-[28rem] overflow-y-auto">
                <table class="w-full text-sm">
                    <thead class="text-left text-gray-500 border-b sticky top-0 bg-white">
                        <tr>
                            <th class="py-1 pr-3">Item</th>
                            <th class="py-1 pr-3">SKU</th>
                            <th class="py-1 pr-3">Price</th>
                            <th class="py-1 pr-3">Stock</th>
                            <th class="py-1"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="row in sellable" :key="row.variant_id" class="border-b last:border-0">
                            <td class="py-1 pr-3">{{ row.label }}</td>
                            <td class="py-1 pr-3 font-mono">{{ row.sku }}</td>
                            <td class="py-1 pr-3">Ksh {{ row.price }}</td>
                            <td class="py-1 pr-3"
                                :class="row.stock <= 0 ? 'text-red-600' : ''">{{ row.stock }}</td>
                            <td class="py-1 text-right">
                                <button @click="addToCart(row)" :disabled="row.stock <= 0"
                                    class="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded px-3 py-1 text-xs">
                                    Add
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>


        <!-- Cart -->
        <div class="bg-white rounded-xl shadow p-5 h-fit">
            <h2 class="font-bold text-lg mb-3">Cart</h2>

            <div v-if="cart.length === 0" class="text-gray-400 italic mb-3">
                Add items from the left.
            </div>

            <div v-for="line in cart" :key="line.variant_id"
                class="flex items-center justify-between gap-2 mb-2 text-sm">
                <div class="flex-1">
                    <div class="font-medium">{{ line.sku }}</div>
                    <div class="text-gray-500">Ksh {{ line.price }} each</div>
                </div>
                <input type="number" min="1" :max="line.stock" v-model.number="line.quantity"
                    @change="clampQty(line)"
                    class="border rounded w-14 px-2 py-1 text-center" />
                <span class="w-20 text-right">Ksh {{ (line.price * line.quantity).toFixed(2) }}</span>
                <button @click="removeLine(line.variant_id)"
                    class="text-red-600 hover:text-red-800">✕</button>
            </div>

            <div class="border-t mt-3 pt-3 flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>Ksh {{ cartTotal.toFixed(2) }}</span>
            </div>

            <div class="mt-4 space-y-2">
                <select v-model="paymentMethod" class="border rounded px-3 py-2 w-full">
                    <option value="cash">Cash</option>
                    <option value="mpesa">M-Pesa</option>
                    <option value="card">Card</option>
                </select>
                <input v-model="customerName" placeholder="Customer name (optional)"
                    class="border rounded px-3 py-2 w-full" />
                <button @click="completeSale" :disabled="submitting || cart.length === 0"
                    class="bg-green-600 hover:bg-green-700 disabled:opacity-40 text-white font-semibold rounded px-4 py-2 w-full">
                    {{ submitting ? "Recording..." : "Complete Sale" }}
                </button>
            </div>
        </div>

    </div>
</div>
</template>
