import { createRouter, createWebHistory } from "vue-router";


const routes = [

    {
        path: "/",
        redirect: "/dashboard"
    },


    {
        path: "/dashboard",
        name:"Dashboard",
        component: () =>
            import("../views/DashboardView.vue")
    },


    {
        path: "/inventory",
        name:"Inventory",
        component: () =>
            import("../views/InventoryView.vue")
    },


    {
        path: "/sell",
        name:"Sell",
        component: () =>
            import("../views/SalesView.vue")
    },


    {
        path: "/reports",
        name:"Reports",
        component: () =>
            import("../views/ReportsView.vue")
    }

];


const router = createRouter({

    history:createWebHistory(),

    routes

});


export default router;