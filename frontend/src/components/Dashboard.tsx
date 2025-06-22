import React, { useEffect, useState } from 'react';
import {
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
} from '@mui/material';
import {
  ShoppingCart as ProductsIcon,
  People as CustomersIcon,
  Receipt as SalesIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
// @ts-ignore
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';

interface DashboardStats {
  totalProducts: number;
  totalCustomers: number;
  totalSales: number;
  totalRevenue: number;
}

const Dashboard: React.FC = () => {
  const { api } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalProducts: 0,
    totalCustomers: 0,
    totalSales: 0,
    totalRevenue: 0,
  });
  const [salesByProduct, setSalesByProduct] = useState<{ name: string; quantity: number }[]>([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [products, customers, sales] = await Promise.all([
          api.get('/products/'),
          api.get('/customers/'),
          api.get('/sales/'),
        ]);

        const totalRevenue = sales.data.reduce(
          (sum: number, sale: any) => sum + sale.total_amount,
          0
        );

        setStats({
          totalProducts: products.data.length,
          totalCustomers: customers.data.length,
          totalSales: sales.data.length,
          totalRevenue,
        });

        // Aggregate sales by product
        const productMap: { [key: number]: { name: string; quantity: number } } = {};
        sales.data.forEach((sale: any) => {
          sale.items.forEach((item: any) => {
            const product = products.data.find((p: any) => p.id === item.product_id);
            if (product) {
              if (!productMap[product.id]) {
                productMap[product.id] = { name: product.name, quantity: 0 };
              }
              productMap[product.id].quantity += item.quantity;
            }
          });
        });
        setSalesByProduct(Object.values(productMap).sort((a, b) => b.quantity - a.quantity));
      } catch (error: unknown) {
        console.error('Error fetching dashboard stats:', error);
      }
    };

    fetchStats();
  }, [api]);

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
  }> = ({ title, value, icon }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {icon}
          <Typography variant="h6" component="div" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div">
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Products"
            value={stats.totalProducts}
            icon={<ProductsIcon color="primary" />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Customers"
            value={stats.totalCustomers}
            icon={<CustomersIcon color="primary" />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Sales"
            value={stats.totalSales}
            icon={<SalesIcon color="primary" />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Revenue"
            value={`$${Number(stats.totalRevenue || 0).toFixed(2)}`}
            icon={<TrendingUpIcon color="primary" />}
          />
        </Grid>
      </Grid>
      {/* Sales by Product Bar Chart */}
      <Box mt={5}>
        <Typography variant="h6" gutterBottom>
          Sales by Product
        </Typography>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={salesByProduct} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Bar dataKey="quantity" fill="#1976d2" name="Quantity Sold" />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default Dashboard; 