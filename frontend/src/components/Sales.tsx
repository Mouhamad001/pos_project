import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Grid,
  Alert,
  Snackbar,
  Tooltip,
  Checkbox,
  FormControlLabel,
  Stack,
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon,
  FileDownload as ExportIcon,
  Calculate as CalculateIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';

interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
}

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
}

interface SaleItem {
  id?: number;
  product_id: number;
  quantity: number;
  product?: Product;
}

interface Sale {
  id: number;
  customer_id: number;
  total_amount: number;
  created_at: string;
  items: SaleItem[];
}

interface ProductSummary {
  id: number;
  name: string;
  totalQuantity: number;
  totalAmount: number;
}

interface CurrentSale {
  customer_id?: number;
  items: SaleItem[];
}

const Sales: React.FC = () => {
  const { api } = useAuth();
  const [sales, setSales] = useState<Sale[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [currentSale, setCurrentSale] = useState<CurrentSale>({ items: [] });
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [quantity, setQuantity] = useState<number>(1);
  const [selectedSales, setSelectedSales] = useState<number[]>([]);
  const [sumDialogOpen, setSumDialogOpen] = useState(false);
  const [sumResult, setSumResult] = useState<number>(0);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [saleToDelete, setSaleToDelete] = useState<number | null>(null);
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [bulkDeleteConfirmOpen, setBulkDeleteConfirmOpen] = useState(false);
  const [selectedCustomerFilter, setSelectedCustomerFilter] = useState<number | ''>('');
  const [selectedProductFilter, setSelectedProductFilter] = useState<number | ''>('');
  const [productsPurchasedOpen, setProductsPurchasedOpen] = useState(false);
  const [productSummary, setProductSummary] = useState<ProductSummary[]>([]);

  useEffect(() => {
    fetchSales();
    fetchProducts();
    fetchCustomers();
  }, [api, startDate, endDate, selectedCustomerFilter, selectedProductFilter]);

  const fetchSales = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate.toISOString());
      if (endDate) params.append('end_date', endDate.toISOString());
      if (selectedCustomerFilter) params.append('customer_id', selectedCustomerFilter.toString());
      if (selectedProductFilter) params.append('product_id', selectedProductFilter.toString());

      const response = await api.get(`/sales?${params.toString()}`);
      setSales(response.data);
    } catch (err: any) {
      console.error('Error fetching sales:', err);
      setError('Failed to fetch sales: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
    } catch (err: any) {
      console.error('Error fetching products:', err);
      setError('Failed to fetch products.');
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers');
      setCustomers(response.data);
    } catch (err: any) {
      console.error('Error fetching customers:', err);
      setError('Failed to fetch customers.');
    }
  };

  const handleOpen = () => {
    setCurrentSale({
      customer_id: undefined,
      items: [],
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (!currentSale.items || currentSale.items.length === 0) {
        setError('At least one product is required.');
        return;
      }

      const saleData = {
        customer_id: currentSale.customer_id || null,
        items: currentSale.items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
        })),
      };

      await api.post('/sales/', saleData);
      setSuccess('Sale created successfully!');
      handleClose();
      fetchSales();
    } catch (err: any) {
      console.error('Error creating sale:', err);
      setError('Failed to create sale: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleAddItem = () => {
    setCurrentSale({
      ...currentSale,
      items: [
        ...(currentSale.items || []),
        { product_id: 0, quantity: 1, product: undefined },
      ],
    });
  };

  const handleRemoveItem = (index: number) => {
    const newItems = [...(currentSale.items || [])];
    newItems.splice(index, 1);
    setCurrentSale({
      ...currentSale,
      items: newItems,
    });
  };

  const handleItemChange = (index: number, field: 'product_id' | 'quantity', value: string | number) => {
    const newItems = [...(currentSale.items || [])];
    newItems[index] = {
      ...newItems[index],
      [field]: field === 'product_id' ? Number(value) : value,
      product: field === 'product_id' ? products.find(p => p.id === Number(value)) : newItems[index].product,
    };
    setCurrentSale({
      ...currentSale,
      items: newItems,
    });
  };

  const handleDeleteClick = (id: number) => {
    setSaleToDelete(id);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (saleToDelete !== null) {
      try {
        await api.delete(`/sales/${saleToDelete}`);
        setSuccess('Sale deleted successfully!');
        fetchSales();
      } catch (err: any) {
        console.error('Error deleting sale:', err);
        setError('Failed to delete sale.');
      } finally {
        setDeleteConfirmOpen(false);
        setSaleToDelete(null);
      }
    }
  };

  const handleDateFilter = () => {
    fetchSales();
    setFilterDialogOpen(false);
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedSales(sales.map(sale => sale.id));
    } else {
      setSelectedSales([]);
    }
  };

  const handleSelectSale = (saleId: number) => {
    setSelectedSales(prev => {
      if (prev.includes(saleId)) {
        return prev.filter(id => id !== saleId);
      } else {
        return [...prev, saleId];
      }
    });
  };

  const handleBulkDelete = async () => {
    try {
      await Promise.all(selectedSales.map(id => api.delete(`/sales/${id}`)));
      setSuccess('Selected sales deleted successfully');
      setSelectedSales([]);
      fetchSales();
    } catch (error: any) {
      console.error('Error deleting sales:', error);
      setError('Failed to delete some sales');
    } finally {
      setBulkDeleteConfirmOpen(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate.toISOString());
      if (endDate) params.append('end_date', endDate.toISOString());
      if (selectedCustomerFilter) params.append('customer_id', selectedCustomerFilter.toString());
      if (selectedProductFilter) params.append('product_id', selectedProductFilter.toString());

      const response = await api.get(`/sales/export/csv?${params.toString()}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sales_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      setSuccess('Sales data exported successfully');
    } catch (error: any) {
      console.error('Error exporting sales:', error);
      setError('Failed to export sales data');
    }
  };

  const handleCalculateSum = () => {
    const filteredSales = sales.filter(sale => {
      const saleDate = new Date(sale.created_at);
      if (startDate && saleDate < startDate) return false;
      if (endDate && saleDate > endDate) return false;
      if (selectedCustomerFilter && sale.customer_id !== selectedCustomerFilter) return false;
      if (selectedProductFilter && !sale.items.some(item => item.product_id === selectedProductFilter)) return false;
      return true;
    });
    const total = filteredSales.reduce((sum, sale) => sum + Number(sale.total_amount), 0);
    setSumResult(total);
    setSumDialogOpen(true);
  };

  const handleProductsPurchased = () => {
    const summary: { [key: number]: ProductSummary } = {};
    
    sales.forEach(sale => {
      sale.items.forEach(item => {
        const product = products.find(p => p.id === item.product_id);
        if (product) {
          if (!summary[product.id]) {
            summary[product.id] = {
              id: product.id,
              name: product.name,
              totalQuantity: 0,
              totalAmount: 0
            };
          }
          summary[product.id].totalQuantity += item.quantity;
          summary[product.id].totalAmount += item.quantity * product.price;
        }
      });
    });

    setProductSummary(Object.values(summary).sort((a, b) => b.totalQuantity - a.totalQuantity));
    setProductsPurchasedOpen(true);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Sales</Typography>
        <Box>
          <Tooltip title="Filter Sales">
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => setFilterDialogOpen(true)}
              sx={{ mr: 1 }}
            >
              Filter
            </Button>
          </Tooltip>
          <Tooltip title="Calculate Total">
            <Button
              variant="outlined"
              startIcon={<CalculateIcon />}
              onClick={handleCalculateSum}
              sx={{ mr: 1 }}
            >
              Calculate Sum
            </Button>
          </Tooltip>
          <Tooltip title="Export to CSV">
            <Button
              variant="outlined"
              startIcon={<ExportIcon />}
              onClick={handleExportCSV}
              sx={{ mr: 1 }}
            >
              Export CSV
            </Button>
          </Tooltip>
          {selectedSales.length > 0 && (
            <Tooltip title="Delete Selected">
              <Button
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => setBulkDeleteConfirmOpen(true)}
                sx={{ mr: 1 }}
              >
                Delete Selected ({selectedSales.length})
              </Button>
            </Tooltip>
          )}
          <Button
            variant="outlined"
            startIcon={<CalculateIcon />}
            onClick={handleProductsPurchased}
            sx={{ mr: 1 }}
          >
            Products Purchased
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpen}
            disabled={loading}
          >
            New Sale
          </Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedSales.length === sales.length && sales.length > 0}
                  indeterminate={selectedSales.length > 0 && selectedSales.length < sales.length}
                  onChange={handleSelectAll}
                />
              </TableCell>
              <TableCell>ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Total Amount</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Items</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sales.map((sale) => (
              <TableRow key={sale.id}>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedSales.includes(sale.id)}
                    onChange={() => handleSelectSale(sale.id)}
                  />
                </TableCell>
                <TableCell>{sale.id}</TableCell>
                <TableCell>
                  {customers.find(c => c.id === sale.customer_id)?.name || 'N/A'}
                </TableCell>
                <TableCell>${Number(sale.total_amount || 0).toFixed(2)}</TableCell>
                <TableCell>{new Date(sale.created_at).toLocaleString()}</TableCell>
                <TableCell>
                  {sale.items.map(item => (
                    <div key={item.id}>
                      {item.product?.name || 'Unknown Product'} x {item.quantity}
                    </div>
                  ))}
                </TableCell>
                <TableCell>
                  <Tooltip title="Delete Sale">
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteClick(sale.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Date and Customer Filter Dialog */}
      <Dialog open={filterDialogOpen} onClose={() => setFilterDialogOpen(false)}>
        <DialogTitle>Filter Sales</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <DatePicker
              label="Start Date"
              value={startDate}
              onChange={(newValue: Date | null) => setStartDate(newValue)}
              renderInput={(params) => <TextField {...params} />}
            />
            <DatePicker
              label="End Date"
              value={endDate}
              onChange={(newValue: Date | null) => setEndDate(newValue)}
              renderInput={(params) => <TextField {...params} />}
            />
          </Stack>
          <FormControl fullWidth sx={{ mt: 3 }}>
            <InputLabel>Customer</InputLabel>
            <Select
              value={selectedCustomerFilter}
              label="Customer"
              onChange={(e) => setSelectedCustomerFilter(e.target.value as number | '')}
            >
              <MenuItem value="">
                <em>All Customers</em>
              </MenuItem>
              {customers.map((customer) => (
                <MenuItem key={customer.id} value={customer.id}>
                  {customer.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth sx={{ mt: 3 }}>
            <InputLabel>Product</InputLabel>
            <Select
              value={selectedProductFilter}
              label="Product"
              onChange={(e) => setSelectedProductFilter(e.target.value as number | '')}
            >
              <MenuItem value="">
                <em>All Products</em>
              </MenuItem>
              {products.map((product) => (
                <MenuItem key={product.id} value={product.id}>
                  {product.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setStartDate(null);
            setEndDate(null);
            setSelectedCustomerFilter('');
            setSelectedProductFilter('');
          }}>
            Clear Filters
          </Button>
          <Button onClick={() => setFilterDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          Are you sure you want to delete this sale?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Delete Confirmation Dialog */}
      <Dialog
        open={bulkDeleteConfirmOpen}
        onClose={() => setBulkDeleteConfirmOpen(false)}
      >
        <DialogTitle>Confirm Bulk Delete</DialogTitle>
        <DialogContent>
          Are you sure you want to delete {selectedSales.length} selected sales?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkDeleteConfirmOpen(false)}>Cancel</Button>
          <Button onClick={handleBulkDelete} color="error">
            Delete All
          </Button>
        </DialogActions>
      </Dialog>

      {/* Sum Result Dialog */}
      <Dialog
        open={sumDialogOpen}
        onClose={() => setSumDialogOpen(false)}
      >
        <DialogTitle>Total Sales Amount</DialogTitle>
        <DialogContent>
          <Typography variant="h6">
            ${Number(sumResult || 0).toFixed(2)}
          </Typography>
          {startDate && endDate && (
            <Typography variant="body2" color="text.secondary">
              For period: {startDate.toLocaleDateString()} - {endDate.toLocaleDateString()}
            </Typography>
          )}
          {selectedCustomerFilter && (
            <Typography variant="body2" color="text.secondary">
              For customer: {customers.find(c => c.id === selectedCustomerFilter)?.name || 'N/A'}
            </Typography>
          )}
          {selectedProductFilter && (
            <Typography variant="body2" color="text.secondary">
              For product: {products.find(p => p.id === selectedProductFilter)?.name || 'N/A'}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSumDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* New Sale Dialog */}
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>New Sale</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <FormControl fullWidth margin="normal">
              <InputLabel id="customer-label">Customer (Optional)</InputLabel>
              <Select
                labelId="customer-label"
                id="customer"
                value={currentSale.customer_id || ''}
                label="Customer (Optional)"
                onChange={(e) => setCurrentSale({ ...currentSale, customer_id: e.target.value ? Number(e.target.value) : undefined })}
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {customers.map((customer) => (
                  <MenuItem key={customer.id} value={customer.id}>
                    {customer.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">Items</Typography>
              {currentSale.items?.map((item, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <FormControl fullWidth>
                    <InputLabel>Product</InputLabel>
                    <Select
                      value={item.product_id || ''}
                      label="Product"
                      onChange={(e) => handleItemChange(index, 'product_id', e.target.value)}
                    >
                      {products.map((product) => (
                        <MenuItem key={product.id} value={product.id}>
                          {product.name} - ${product.price}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <TextField
                    type="number"
                    label="Quantity"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value))}
                    inputProps={{ min: 1 }}
                    sx={{ width: '100px' }}
                  />
                  <IconButton onClick={() => handleRemoveItem(index)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
              <Button
                startIcon={<AddIcon />}
                onClick={handleAddItem}
                variant="outlined"
                sx={{ mt: 1 }}
              >
                Add Item
              </Button>
            </Box>

            <Typography variant="h6" sx={{ mt: 2 }}>
              Total: ${currentSale.items?.reduce((sum, item) => sum + ((typeof item.product?.price === 'number' ? item.product?.price : Number(item.product?.price || 0)) * item.quantity), 0).toFixed(2)}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button type="submit" variant="contained" onClick={handleSubmit}>
            Create Sale
          </Button>
        </DialogActions>
      </Dialog>

      {/* Products Purchased Dialog */}
      <Dialog
        open={productsPurchasedOpen}
        onClose={() => setProductsPurchasedOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Products Purchased Summary</DialogTitle>
        <DialogContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product Name</TableCell>
                  <TableCell align="right">Total Quantity</TableCell>
                  <TableCell align="right">Total Amount</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {productSummary.map((product) => (
                  <TableRow key={product.id}>
                    <TableCell>{product.name}</TableCell>
                    <TableCell align="right">{product.totalQuantity}</TableCell>
                    <TableCell align="right">${product.totalAmount.toFixed(2)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProductsPurchasedOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={!!error || !!success}
        autoHideDuration={6000}
        onClose={() => {
          setError(null);
          setSuccess(null);
        }}
      >
        <Alert
          onClose={() => {
            setError(null);
            setSuccess(null);
          }}
          severity={error ? "error" : "success"}
          sx={{ width: '100%' }}
        >
          {error || success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Sales; 