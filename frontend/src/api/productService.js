import api from "./axios";


export default {


    async getProducts(includeInactive = false) {

        const response = await api.get("/products/", {
            params: { include_inactive: includeInactive }
        })

        return response.data

    },


    async createProduct(product) {

        const response = await api.post("/products/", product)

        return response.data

    },


    async updateProduct(id, changes) {

        const response = await api.put(`/products/${id}`, changes)

        return response.data

    },


    async archiveProduct(id) {

        const response = await api.delete(`/products/${id}`)

        return response.data

    }

}
