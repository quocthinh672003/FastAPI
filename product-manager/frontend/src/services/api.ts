import axios from "axios";
import { Product, ProductCreate, ProductUpdate } from "../types/product";

const API_URL = "http://localhost:8000/api/v1";

const api = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    }
})

export const ProductAPI = {
    getProducts: async (skip: number, limit: number, search: string): Promise<Product[]> => {
        const response = await api.get("/products", {
            params: { skip, limit, search },
        });
        return response.data;
    },

    createProduct: async (product: ProductCreate): Promise<Product> => {
        const response = await api.post('/products', product);
        return response.data;
    },

    updateProduct: async (productId: number, product: ProductUpdate): Promise<Product> => {
        const response = await api.put(`/products/${productId}`, {
            ...product,
        });
        return response.data;
    },

    deleteProduct: async (productId: number): Promise<void> => {
        await api.delete(`/products/${productId}`);
    },
}

export default ProductAPI;