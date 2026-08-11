<script setup>

import BaseBadge from "../common/BaseBadge.vue"


const products=[
{
id:1,
name:"Black Hoodie",
category:"Hoodies",
size:"L",
color:"Black",
quantity:20,
price:35
},
{
id:2,
name:"Blue Jeans",
category:"Pants",
size:"M",
color:"Blue",
quantity:3,
price:40
}
]


</script>


<template>


<div

class="
bg-white
rounded-2xl
border
border-slate-200
overflow-hidden
shadow-sm
"

>


<div class="
p-5
border-b
border-slate-200
">

<h2 class="
font-semibold
text-lg
">

Products

</h2>

</div>



<div class="overflow-x-auto">


<table class="
w-full
text-sm
">


<thead class="
bg-slate-50
text-slate-600
">


<tr>


<th class="p-4 text-left">
Product
</th>


<th class="p-4">
Category
</th>


<th class="p-4">
Size
</th>


<th class="p-4">
Color
</th>


<th class="p-4">
Quantity
</th>


<th class="p-4">
Price
</th>


<th class="p-4">
Status
</th>


<th class="p-4">
Actions
</th>


</tr>


</thead>



<tbody>


<tr

v-for="product in products"

:key="product.id"

class="
border-t
border-slate-100
hover:bg-slate-50
"

>


<td class="p-4 font-medium">

{{product.name}}

</td>


<td class="p-4">

{{product.category}}

</td>


<td class="p-4">

{{product.size}}

</td>


<td class="p-4">

{{product.color}}

</td>


<td class="p-4">

{{product.quantity}}

</td>


<td class="p-4">

${{product.price}}

</td>


<td class="p-4">

<BaseBadge
:status="
product.quantity < 5
? 'Low Stock'
: 'Available'
"
/>

</td>


<td class="p-4">


<button

class="
text-blue-600
hover:underline
"

>

Edit

</button>


</td>


</tr>


</tbody>



</table>


</div>


</div>


</template>