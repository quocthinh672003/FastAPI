import React from 'react';
import { Product, ProductUpdate } from '../types/product';
import { Card, CardContent, Typography, Button } from '@mui/material';
import { useState } from 'react';
import { ProductAPI } from '../services/api';
import { Snackbar, Alert } from '@mui/material';
import { styled } from '@mui/material/styles';

interface ProductItemProps {
    product: Product;
    onUpdate: (product: Product) => void;
    onDelete: (id: number) => void;
}

const ProductItem: React.FC<ProductItemProps> = ({ product, onUpdate, onDelete}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editedProduct, setEditedProduct] = useState<ProductUpdate>(
        {
            name: product.name,
            description: product.description,
            price: product.price,
            category: product.category,
        } 
    );
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [openSnackbar, setOpenSnackbar] = useState(false);

    const handleUpdate = async () => {
        try {
            const updatedProduct = await ProductAPI.updateProduct(product.id, editedProduct);
            

        } catch (error) {
            
        }
    }
}