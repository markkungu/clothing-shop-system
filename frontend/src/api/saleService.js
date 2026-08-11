import api from "./axios";


export default {


    async createSale(sale) {

        const response = await api.post("/sales/", sale)

        return response.data

    },


    async getSales(days = 7) {

        const response = await api.get("/sales/", {
            params: { days }
        })

        return response.data

    },


    async getSummary(days = 7) {

        const response = await api.get("/sales/summary", {
            params: { days }
        })

        return response.data

    }

}
