<script setup>

const stats = [
    {
        title:"Total Products",
        value:"120",
        icon:"📦"
    },
    {
        title:"Low Stock",
        value:"15",
        icon:"⚠️"
    },
    {
        title:"Categories",
        value:"8",
        icon:"🏷️"
    },
    {
        title:"Inventory Value",
        value:"$20,000",
        icon:"💰"
    }
]

</script>


<template>

<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">


    <div
    v-for="item in stats"
    :key="item.title"
    class="
    bg-white
    rounded-2xl
    border
    border-slate-200
    p-6
    shadow-sm
    hover:shadow-md
    transition
    "
    >


        <div class="flex justify-between items-center">


            <div>

                <p class="
                text-sm
                text-slate-500
                ">
                    {{ item.title }}
                </p>


                <h2 class="
                text-3xl
                font-bold
                mt-3
                text-slate-900
                ">
                    {{ item.value }}
                </h2>

            </div>


            <div class="
            w-12
            h-12
            rounded-xl
            bg-slate-100
            flex
            items-center
            justify-center
            text-xl
            ">
                {{ item.icon }}
            </div>


        </div>


    </div>


</div>


</template>