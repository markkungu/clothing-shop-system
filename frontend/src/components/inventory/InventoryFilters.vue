<script setup>


defineEmits([
    "search",
    "filter",
    "add-product"
])


</script>


<template>


<div
class="
bg-white
rounded-2xl
border
border-slate-200
p-5
shadow-sm
"
>


<div
class="
flex
flex-col
lg:flex-row
gap-4
justify-between
"
>


<div class="
flex
flex-col
sm:flex-row
gap-4
flex-1
">


<input

class="
w-full
sm:w-72
px-4
py-3
rounded-xl
border
border-slate-200
outline-none
focus:ring-2
focus:ring-slate-900
"

placeholder="Search products..."


@input="$emit('search',$event.target.value)"

>



<select

class="
px-4
py-3
rounded-xl
border
border-slate-200
outline-none
"

@change="$emit('filter',$event.target.value)"

>


<option>
All Categories
</option>

<option>
Shirts
</option>

<option>
Pants
</option>

<option>
Shoes
</option>


</select>



</div>



<button

class="
bg-slate-900
text-white
px-5
py-3
rounded-xl
font-medium
hover:bg-slate-800
transition
"

@click="$emit('add-product')"

>

+ Add Product

</button>



</div>


</div>


</template>