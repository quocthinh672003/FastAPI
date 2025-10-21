# 🛍️ Hướng Dẫn Xây Dựng Ứng Dụng Quản Lý Sản Phẩm
## Full-Stack React + FastAPI

---

## 📋 **MỤC LỤC**

1. [Tổng Quan Bài Tập](#tổng-quan-bài-tập)
2. [Cấu Trúc Project](#cấu-trúc-project)
3. [Backend - FastAPI](#backend---fastapi)
4. [Frontend - React](#frontend---react)
5. [Chạy Ứng Dụng](#chạy-ứng-dụng)
6. [Kiến Thức Học Được](#kiến-thức-học-được)

---

## 🎯 **TỔNG QUAN BÀI TẬP**

### **Mô tả:**
Xây dựng ứng dụng web quản lý sản phẩm với:
- **Backend (FastAPI)**: API REST để quản lý sản phẩm
- **Frontend (React)**: Giao diện người dùng
- **Database (PostgreSQL)**: Lưu trữ dữ liệu

### **Tính năng:**
- ✅ Xem danh sách sản phẩm
- ✅ Thêm sản phẩm mới
- ✅ Cập nhật sản phẩm
- ✅ Xóa sản phẩm
- ✅ Tìm kiếm sản phẩm

---

## 📁 **CẤU TRÚC PROJECT**

```
product-manager/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Cấu hình database
│   │   │   └── database.py        # Kết nối database
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── product.py         # Model sản phẩm
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── product.py        # Pydantic schemas
│   │   └── api/
│   │       ├── __init__.py
│   │       └── products.py       # API endpoints
│   ├── main.py                   # Entry point
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ProductList.tsx   # Hiển thị danh sách
    │   │   ├── ProductForm.tsx   # Form thêm/sửa
    │   │   └── ProductItem.tsx   # Item sản phẩm
    │   ├── services/
    │   │   └── api.ts            # API calls
    │   ├── types/
    │   │   └── product.ts        # TypeScript types
    │   ├── App.tsx
    │   └── index.tsx
    └── package.json
```

---

## 🔧 **BACKEND - FASTAPI**

### **Bước 1: Tạo cấu trúc thư mục**

```bash
mkdir product-manager
cd product-manager
mkdir backend
cd backend
mkdir app
cd app
mkdir core models schemas api
```

### **Bước 2: Tạo requirements.txt**

**File: `backend/requirements.txt`**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-multipart==0.0.6
```

### **Bước 3: Tạo database configuration**

**File: `backend/app/core/config.py`**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:password@localhost:5432/productdb"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**File: `backend/app/core/database.py`**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **Bước 4: Tạo Product model**

**File: `backend/app/models/product.py`**
```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### **Bước 5: Tạo Pydantic schemas**

**File: `backend/app/schemas/product.py`**
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### **Bước 6: Tạo API endpoints**

**File: `backend/app/api/products.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()

@router.get("/products", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}
```

### **Bước 7: Tạo main.py**

**File: `backend/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.products import router as products_router

app = FastAPI(title="Product Manager API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Product Manager API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## ⚛️ **FRONTEND - REACT**

### **Bước 1: Tạo React project**

```bash
cd ..
npx create-react-app frontend --template typescript
cd frontend
npm install axios
```

### **Bước 2: Tạo TypeScript types**

**File: `frontend/src/types/product.ts`**
```typescript
export interface Product {
  id: number;
  name: string;
  description?: string;
  price: number;
  category?: string;
  created_at: string;
  updated_at?: string;
}

export interface ProductCreate {
  name: string;
  description?: string;
  price: number;
  category?: string;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  category?: string;
}
```

### **Bước 3: Tạo API service**

**File: `frontend/src/services/api.ts`**
```typescript
import axios from 'axios';
import { Product, ProductCreate, ProductUpdate } from '../types/product';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const productAPI = {
  getProducts: async (search?: string): Promise<Product[]> => {
    const response = await api.get('/products', {
      params: { search }
    });
    return response.data;
  },
  
  createProduct: async (product: ProductCreate): Promise<Product> => {
    const response = await api.post('/products', product);
    return response.data;
  },
  
  updateProduct: async (id: number, product: ProductUpdate): Promise<Product> => {
    const response = await api.put(`/products/${id}`, product);
    return response.data;
  },
  
  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`);
  },
};

export default api;
```

### **Bước 4: Tạo ProductItem component**

**File: `frontend/src/components/ProductItem.tsx`**
```typescript
import React, { useState } from 'react';
import { Product, ProductUpdate } from '../types/product';
import { productAPI } from '../services/api';

interface ProductItemProps {
  product: Product;
  onUpdate: (product: Product) => void;
  onDelete: (id: number) => void;
}

const ProductItem: React.FC<ProductItemProps> = ({ product, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<ProductUpdate>({
    name: product.name,
    description: product.description,
    price: product.price,
    category: product.category,
  });

  const handleSave = async () => {
    try {
      const updatedProduct = await productAPI.updateProduct(product.id, editData);
      onUpdate(updatedProduct);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update product:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productAPI.deleteProduct(product.id);
        onDelete(product.id);
      } catch (error) {
        console.error('Failed to delete product:', error);
      }
    }
  };

  return (
    <div className="border p-4 rounded-lg shadow-md">
      {isEditing ? (
        <div className="space-y-2">
          <input
            type="text"
            value={editData.name}
            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
            className="w-full p-2 border rounded"
          />
          <textarea
            value={editData.description}
            onChange={(e) => setEditData({ ...editData, description: e.target.value })}
            className="w-full p-2 border rounded"
            rows={2}
          />
          <input
            type="number"
            value={editData.price}
            onChange={(e) => setEditData({ ...editData, price: parseFloat(e.target.value) })}
            className="w-full p-2 border rounded"
          />
          <input
            type="text"
            value={editData.category}
            onChange={(e) => setEditData({ ...editData, category: e.target.value })}
            className="w-full p-2 border rounded"
          />
          <div className="flex space-x-2">
            <button onClick={handleSave} className="bg-blue-500 text-white px-4 py-2 rounded">
              Save
            </button>
            <button onClick={() => setIsEditing(false)} className="bg-gray-500 text-white px-4 py-2 rounded">
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div>
          <h3 className="text-lg font-semibold">{product.name}</h3>
          <p className="text-gray-600">{product.description}</p>
          <p className="text-green-600 font-bold">${product.price}</p>
          <p className="text-sm text-gray-500">{product.category}</p>
          <div className="flex space-x-2 mt-2">
            <button onClick={() => setIsEditing(true)} className="bg-yellow-500 text-white px-3 py-1 rounded">
              Edit
            </button>
            <button onClick={handleDelete} className="bg-red-500 text-white px-3 py-1 rounded">
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductItem;
```

### **Bước 5: Tạo ProductForm component**

**File: `frontend/src/components/ProductForm.tsx`**
```typescript
import React, { useState } from 'react';
import { ProductCreate } from '../types/product';

interface ProductFormProps {
  onSubmit: (product: ProductCreate) => void;
}

const ProductForm: React.FC<ProductFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<ProductCreate>({
    name: '',
    description: '',
    price: 0,
    category: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({ name: '', description: '', price: 0, category: '' });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg">
      <h3 className="text-lg font-semibold">Add New Product</h3>
      
      <div>
        <label className="block text-sm font-medium">Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full p-2 border rounded"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full p-2 border rounded"
          rows={2}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium">Price</label>
        <input
          type="number"
          step="0.01"
          value={formData.price}
          onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
          className="w-full p-2 border rounded"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium">Category</label>
        <input
          type="text"
          value={formData.category}
          onChange={(e) => setFormData({ ...formData, category: e.target.value })}
          className="w-full p-2 border rounded"
        />
      </div>
      
      <button type="submit" className="bg-green-500 text-white px-4 py-2 rounded">
        Add Product
      </button>
    </form>
  );
};

export default ProductForm;
```

### **Bước 6: Tạo ProductList component**

**File: `frontend/src/components/ProductList.tsx`**
```typescript
import React, { useState, useEffect } from 'react';
import { Product, ProductCreate } from '../types/product';
import { productAPI } from '../services/api';
import ProductItem from './ProductItem';
import ProductForm from './ProductForm';

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const data = await productAPI.getProducts(searchTerm);
      setProducts(data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async (productData: ProductCreate) => {
    try {
      const newProduct = await productAPI.createProduct(productData);
      setProducts([...products, newProduct]);
    } catch (error) {
      console.error('Failed to create product:', error);
    }
  };

  const handleUpdateProduct = (updatedProduct: Product) => {
    setProducts(products.map(p => p.id === updatedProduct.id ? updatedProduct : p));
  };

  const handleDeleteProduct = (id: number) => {
    setProducts(products.filter(p => p.id !== id));
  };

  const handleSearch = () => {
    fetchProducts();
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Product Manager</h1>
      
      {/* Search */}
      <div className="mb-6">
        <div className="flex space-x-2">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search products..."
            className="flex-1 p-2 border rounded"
          />
          <button onClick={handleSearch} className="bg-blue-500 text-white px-4 py-2 rounded">
            Search
          </button>
        </div>
      </div>
      
      {/* Add Product Form */}
      <div className="mb-6">
        <ProductForm onSubmit={handleCreateProduct} />
      </div>
      
      {/* Products List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map(product => (
          <ProductItem
            key={product.id}
            product={product}
            onUpdate={handleUpdateProduct}
            onDelete={handleDeleteProduct}
          />
        ))}
      </div>
      
      {products.length === 0 && (
        <div className="text-center text-gray-500 mt-8">
          No products found. Add your first product!
        </div>
      )}
    </div>
  );
};

export default ProductList;
```

### **Bước 7: Cập nhật App.tsx**

**File: `frontend/src/App.tsx`**
```typescript
import React from 'react';
import ProductList from './components/ProductList';
import './App.css';

function App() {
  return (
    <div className="App">
      <ProductList />
    </div>
  );
}

export default App;
```

---

## 🚀 **CHẠY ỨNG DỤNG**

### **Bước 1: Setup Database**

```bash
# Tạo database PostgreSQL
createdb productdb

# Hoặc dùng Docker
docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=productdb -p 5432:5432 -d postgres
```

### **Bước 2: Chạy Backend**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Kết quả:**
- API chạy tại: `http://localhost:8000`
- API docs tại: `http://localhost:8000/docs`

### **Bước 3: Chạy Frontend**

```bash
cd frontend
npm start
```

**Kết quả:**
- Frontend chạy tại: `http://localhost:3000`

---

## 📚 **KIẾN THỨC HỌC ĐƯỢC**

### **Backend (FastAPI):**
1. **API Design**: RESTful endpoints, HTTP methods
2. **Database**: SQLAlchemy ORM, models, relationships
3. **Validation**: Pydantic schemas, data validation
4. **Dependency Injection**: Database sessions, routers
5. **CORS**: Cross-origin resource sharing

### **Frontend (React):**
1. **Components**: Functional components, props, state
2. **Hooks**: useState, useEffect, custom hooks
3. **API Integration**: Axios, HTTP requests
4. **TypeScript**: Type safety, interfaces
5. **State Management**: Local state, lifting state up

### **Full-Stack Integration:**
1. **API Communication**: Frontend ↔ Backend
2. **Error Handling**: Try-catch, error states
3. **Loading States**: User feedback
4. **CRUD Operations**: Create, Read, Update, Delete
5. **Search Functionality**: Filtering data

---

## 🎯 **KẾT QUẢ MONG ĐỢI**

Sau khi hoàn thành, bạn sẽ có:
- ✅ Ứng dụng web hoàn chỉnh
- ✅ API REST với 5 endpoints
- ✅ Giao diện React responsive
- ✅ Chức năng CRUD đầy đủ
- ✅ Tìm kiếm sản phẩm
- ✅ Dữ liệu lưu trong PostgreSQL

---

## 💡 **TIPS QUAN TRỌNG**

1. **Bắt đầu từ Backend**: API trước, UI sau
2. **Test từng bước**: Không code quá nhiều cùng lúc
3. **Đọc Documentation**: FastAPI docs và React docs
4. **Debug thường xuyên**: Console.log và print statements
5. **Commit thường xuyên**: Git để backup code

---

**Chúc bạn học tập hiệu quả! 🎉**
