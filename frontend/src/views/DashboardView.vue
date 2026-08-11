<script setup>

import { ref, computed, onMounted } from "vue"
import { RouterLink } from "vue-router"

import productService from "../api/productService"
import saleService from "../api/saleService"


const products = ref([])
const week = ref(null)
const today = ref(null)
const loading = ref(false)
const errorMsg = ref("")


const load = async () => {
    try {
        loading.value = true
        errorMsg.value = ""
        const [p, w, t] = await Promise.all([
            productService.getProducts(false),
            saleService.getSummary(7),
            saleService.getSummary(1)
        ])
        products.value = p
        week.value = w
        today.value = t
    } catch (e) {
        console.log(e)
        errorMsg.value = "Could not load dashboard data."
    } finally {
        loading.value = false
    }
}


// Flatten active variants for stock math
const variants = computed(() =>
    products.value.flatMap(p =>
        p.variants
            .filter(v => v.is_active)
            .map(v => ({ ...v, product_name: p.name }))
    )
)

const totalUnits = computed(() =>
    variants.value.reduce((s, v) => s + (v.stock_quantity || 0), 0)
)

const inventoryValue = computed(() =>
    variants.value.reduce((s, v) => s + Number(v.price) * (v.stock_quantity || 0), 0)
)

const lowStock = computed(() =>
    variants.value
        .filter(v => v.stock_quantity <= v.reorder_level)
        .sort((a, b) => a.stock_quantity - b.stock_quantity)
)

const fmt = (n) => Number(n).toLocaleString("en-KE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })


onMounted(load)

</script>



<template>
<div class="p-6 max-w-6xl mx-auto">

    <h1 class="text-3xl font-bold mb-6">Dashboard</h1>

    <p v-if="errorMsg" class="mb-4 rounded-lg bg-red-100 text-red-700 px-4 py-2">{{ errorMsg }}</p>

    <div v-if="loading" class="text-gray-500">Loading...</div>

    <template v-else>

        <!-- KPI cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-xl shadow p-5">
                <div class="text-gray-500 text-sm">Items in stock</div>
                <div class="text-2xl font-bold">{{ totalUnits }}</div>
            </div>
            <div class="bg-white rounded-xl shadow p-5">
                <div class="text-gray-500 text-sm">Inventory value (retail)</div>
                <div class="text-2xl font-bold">Ksh {{ fmt(inventoryValue) }}</div>
            </div>
            <div class="bg-white rounded-xl shadow p-5">
                <div class="text-gray-500 text-sm">Sales today</div>
                <div class="text-2xl font-bold">
                    {{ today?.sale_count ?? 0 }}
                    <span class="text-base font-normal text-gray-400">· Ksh {{ fmt(today?.revenue ?? 0) }}</span>
                </div>
            </div>
            <div class="bg-white rounded-xl shadow p-5">
                <div class="text-gray-500 text-sm">Profit (7 days)</div>
                <div class="text-2xl font-bold text-green-700">Ksh {{ fmt(week?.profit ?? 0) }}</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

            <!-- Low stock alerts -->
            <div class="bg-white rounded-xl shadow p-5">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="font-bold text-lg">⚠ Reorder alerts</h2>
                    <RouterLink to="/inventory" class="text-blue-600 text-sm">Manage →</RouterLink>
                </div>
                <div v-if="lowStock.length === 0" class="text-gray-400 italic">
                    All stock is above reorder levels. 👍
                </div>
                <table v-else class="w-full text-sm">
                    <thead class="text-left text-gray-500 border-b">
                        <tr><th class="py-1">Item</th><th class="py-1">SKU</th><th class="py-1 text-right">Stock</th><th class="py-1 text-right">Reorder at</th></tr>
                    </thead>
                    <tbody>
                        <tr v-for="v in lowStock" :key="v.id" class="border-b last:border-0">
                            <td class="py-1">{{ v.product_name }} <span class="text-gray-400">{{ v.size }} {{ v.color }}</span></td>
                            <td class="py-1 font-mono">{{ v.sku }}</td>
                            <td class="py-1 text-right text-red-600 font-semibold">{{ v.stock_quantity }}</td>
                            <td class="py-1 text-right text-gray-500">{{ v.reorder_level }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Quick actions -->
            <div class="bg-white rounded-xl shadow p-5">
                <h2 class="font-bold text-lg mb-3">Quick actions</h2>
                <div class="grid grid-cols-1 gap-3">
                    <RouterLink to="/sell"
                        class="block bg-green-600 hover:bg-green-700 text-white font-semibold rounded px-4 py-3 text-center">
                        🛒 Record a sale
                    </RouterLink>
                    <RouterLink to="/inventory"
                        class="block bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded px-4 py-3 text-center">
                        📦 Add / restock inventory
                    </RouterLink>
                    <RouterLink to="/reports"
                        class="block bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded px-4 py-3 text-center">
                        📊 View sales reports
                    </RouterLink>
                </div>
            </div>

        </div>

    </template>
</div>
</template>
