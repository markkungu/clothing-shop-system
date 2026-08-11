import api from "./axios";


export default {


    async addVariant(productId, variant) {

        const response = await api.post(
            `/products/${productId}/variants/`,
            variant
        )

        return response.data

    },


    async updateVariant(id, changes) {

        const response = await api.put(`/variants/${id}`, changes)

        return response.data

    },


    async archiveVariant(id) {

        const response = await api.delete(`/variants/${id}`)

        return response.data

    }

}
