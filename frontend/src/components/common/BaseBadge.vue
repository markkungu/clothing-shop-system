<script setup>


defineProps({

status:{
    type:String,
    default:"Available"
}

})


</script>


<template>


<span

class="
px-3
py-1
rounded-full
text-xs
font-medium
"

:class="{

'bg-green-100 text-green-700':
status==='Available',

'bg-yellow-100 text-yellow-700':
status==='Low Stock',

'bg-red-100 text-red-700':
status==='Out Of Stock'

}"

>

{{status}}

</span>


</template>