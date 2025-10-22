export interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    category: string;
    created_at: string;
    updated_at: string;
}
export interface ProductCreate {
    name: string;
    description: string;
    price: number;
    category: string;
}
export interface ProductUpdate {
    name?: string;
    description?: string;
    price?: number;
    category?: string;
}
