<template>

<div class="flex min-h-screen bg-slate-50">


    <AppSidebar />


    <div class="flex-1">


        <AppHeader />


        <main class="
            p-6
            lg:p-8
        ">

            <slot />

        </main>


    </div>


</div>


</template>