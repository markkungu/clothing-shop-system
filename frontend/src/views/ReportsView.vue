<script setup>

import { ref, onMounted } from "vue"

import saleService from "../api/saleService"


const summary = ref(null)
const sales = ref([])
const days = ref(7)
const loading = ref(false)
const errorMsg = ref("")
const expanded = ref(null)   // sale id whose items are shown


const load = async () => {
    try {
        loading.value = true
        errorMsg.value = ""
        const [s, list] = await Promise.all([
            saleService.getSummary(days.value),
            saleService.getSales(days.value)
        ])
        summary.value = s
        sales.value = list
    } catch (e) {
        console.log(e)
        errorMsg.value = "Could not load sales reports."
    } finally {
        loading.value = false
    }
}

const setDays = (d) => { days.value = d; load() }

const toggle = (id) => { expanded.value = expanded.value === id ? null : id }

const fmt = (n) => Number(n).toLocaleString("en-KE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fmtDate = (iso) => new Date(iso).toLocaleString("en-KE", {
    year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
})


onMounted(load)

</script>



<template>
<div class="p-6 max-w-6xl mx-auto">

    <div class="flex items-center justify-between mb-6">
        <h1 class="text-3xl font-bold">Sales &amp; Reports</h1>
        <div class="flex gap-2">
            <button v-for="d in [7, 30, 90]" :key="d" @click="setDays(d)"
                :class="days === d ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'"
                class="rounded px-3 py-1 text-sm">
                Last {{ d }} days
            </button>
        </div>
    </div>

    <p v-if="errorMsg" class="mb-4 rounded-lg bg-red-100 text-red-700 px-4 py-2">
        {{ errorMsg }}
    </p>

    <div v-if="loading" class="text-gray-500">Loading...</div>

    <template v-else-if="summary">

        <!-- Summary cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-xl shadow p-5">
                <div class="text-gray-500 text-sm">Revenue</div>
                <div class="text-2xl font-bold">Ksh {{ fmt(summary.revenue) }}</div>
            </div>
            <div class="bg-white rounded-xl shadow p-5">
                <div class="text-gray-500 text-sm">Profit</div>
                <div class="text-2xl font-bold text-green-700">Ksh {{ fmt(summary.profit) }}</div>
            </div>
            <div class="bg-white rounded-xl shadow p-5">
                <div class="text-gray-500 text-sm">Sales</div>
                <div class="text-2xl font-bold">{{ summary.sale_count }}</div>
            </div>
            <div class="bg-white rounded-xl shadow p-5">
                <div class="text-gray-500 text-sm">Items sold</div>
                <div class="text-2xl font-bold">{{ summary.items_sold }}</div>
            </div>
        </div>


        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">

            <!-- Per-day breakdown -->
            <div class="bg-white rounded-xl shadow p-5">
                <h2 class="font-bold text-lg mb-3">Daily breakdown</h2>
                <table class="w-full text-sm">
                    <thead class="text-left text-gray-500 border-b">
                        <tr><th class="py-1">Day</th><th class="py-1">Sales</th><th class="py-1">Items</th><th class="py-1 text-right">Revenue</th><th class="py-1 text-right">Profit</th></tr>
                    </thead>
                    <tbody>
                        <tr v-for="d in summary.daily" :key="d.day" class="border-b last:border-0">
                            <td class="py-1">{{ d.day }}</td>
                            <td class="py-1">{{ d.sale_count }}</td>
                            <td class="py-1">{{ d.items_sold }}</td>
                            <td class="py-1 text-right">Ksh {{ fmt(d.revenue) }}</td>
                            <td class="py-1 text-right text-green-700">Ksh {{ fmt(d.profit) }}</td>
                        </tr>
                        <tr v-if="summary.daily.length === 0">
                            <td colspan="5" class="py-2 text-gray-400 italic">No sales in this period.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Top sellers -->
            <div class="bg-white rounded-xl shadow p-5">
                <h2 class="font-bold text-lg mb-3">Top sellers</h2>
                <table class="w-full text-sm">
                    <thead class="text-left text-gray-500 border-b">
                        <tr><th class="py-1">SKU</th><th class="py-1">Item</th><th class="py-1">Qty</th><th class="py-1 text-right">Revenue</th></tr>
                    </thead>
                    <tbody>
                        <tr v-for="t in summary.top_products" :key="t.sku" class="border-b last:border-0">
                            <td class="py-1 font-mono">{{ t.sku }}</td>
                            <td class="py-1">{{ t.product_name }}</td>
                            <td class="py-1">{{ t.quantity_sold }}</td>
                            <td class="py-1 text-right">Ksh {{ fmt(t.revenue) }}</td>
                        </tr>
                        <tr v-if="summary.top_products.length === 0">
                            <td colspan="4" class="py-2 text-gray-400 italic">No sales yet.</td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </div>


        <!-- Recent sales audit trail -->
        <div class="bg-white rounded-xl shadow p-5">
            <h2 class="font-bold text-lg mb-3">Recent sales</h2>
            <p class="text-gray-500 text-sm mb-3">
                Every purchase is recorded here — reconcile this against the cash drawer.
            </p>

            <div v-if="sales.length === 0" class="text-gray-400 italic">No sales recorded yet.</div>

            <div v-for="s in sales" :key="s.id" class="border-b last:border-0 py-2">
                <button @click="toggle(s.id)"
                    class="w-full flex items-center justify-between text-left">
                    <span>
                        <span class="font-semibold">Sale #{{ s.id }}</span>
                        <span class="text-gray-500 text-sm ml-2">{{ fmtDate(s.created_at) }}</span>
                        <span class="text-gray-400 text-sm ml-2">· {{ s.payment_method }}</span>
                        <span v-if="s.customer_name" class="text-gray-400 text-sm ml-1">· {{ s.customer_name }}</span>
                    </span>
                    <span class="font-bold">Ksh {{ fmt(s.total_amount) }}</span>
                </button>

                <ul v-if="expanded === s.id" class="mt-2 ml-4 text-sm text-gray-600 list-disc">
                    <li v-for="i in s.items" :key="i.id">
                        {{ i.quantity }} × {{ i.product_name }} ({{ i.sku }}) @ Ksh {{ fmt(i.unit_price) }}
                        = Ksh {{ fmt(i.line_total) }}
                    </li>
                </ul>
            </div>
        </div>

    </template>
</div>
</template>
