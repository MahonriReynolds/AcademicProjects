// hold items
let itemsList = [];

// fetch internal api
async function fetchProducts() {
    try {
        const response = await fetch('/api/form-product-data');
        if (response.ok) {
            const data = await response.json();
            return data.products; // get products with id, name, and unit
        } else {
            console.error('Failed to fetch products');
        }
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

// init product data and listener
async function init() {
    const products = await fetchProducts();
    if (products && products.length > 0) {
        // add item button listen
        document.getElementById('add-item-btn').addEventListener('click', function() {
            addItem(products);
        });

        // init blank item
        addItem(products);
    }
}

// add item
function addItem(products) {
    const itemSection = document.getElementById('items-section');
    const newItem = document.createElement('div');
    newItem.classList.add('item-entry');

    const itemCount = itemsList.length + 1;

    const newItemHTML = `
        <label for="product-${itemCount}">Product</label>
        <select name="product-${itemCount}" id="product-${itemCount}" class="product-select" required>
            <option value="" disabled selected>Select a Product</option>
            ${products.map(product => `<option value="${product.id}" data-unit="${product.unit}">${product.name}</option>`).join('')}
        </select>

        <label for="usage-date-${itemCount}">Usage Date</label>
        <input type="date" id="usage-date-${itemCount}" name="usage-date-${itemCount}" required>

        <label for="amount-${itemCount}">Amount</label>
        <input type="number" id="amount-${itemCount}" name="amount-${itemCount}" required min="0.01" step="any" oninput="validateAmount(this)">

        <span id="unit-${itemCount}" class="unit" style="color: blue; font-weight: bold;"></span>

        <button type="button" onclick="removeItem(this)">Remove Item</button>
    `;

    newItem.innerHTML = newItemHTML;
    itemSection.appendChild(newItem);

    // store item
    itemsList.push(newItem);

    // Initialize Select2 for the new product select field
    const productSelect = newItem.querySelector(`#product-${itemCount}`);
    $(productSelect).select2({
        width: '100%', // Make the dropdown match the full width
        placeholder: "Search for a product...",
        allowClear: true // Allow clearing selection
    });

    // Update unit when a product is selected
    productSelect.addEventListener('change', function () {
        const selectedProduct = products.find(product => product.id === productSelect.value);
        const unitSpan = document.getElementById(`unit-${itemCount}`);
        
        if (selectedProduct) {
            unitSpan.textContent = `Unit: ${selectedProduct.unit}`;
        } else {
            unitSpan.textContent = '';  // Clear the unit if no product is selected
        }
    });
}


function validateAmount(inputElement) {
    const value = inputElement.value;

    // Check if the value is a valid positive number and greater than or equal to 0.01
    if (value <= 0) {
        inputElement.setCustomValidity('Please enter a positive number.');
        inputElement.reportValidity();  // Show the validation message
    } else {
        inputElement.setCustomValidity('');
    }
}

// remove item
function removeItem(button) {
    const itemSection = document.getElementById('items-section');
    const itemToRemove = button.closest('.item-entry');
    const index = itemsList.indexOf(itemToRemove);
    if (index !== -1) {
        itemsList.splice(index, 1);
    }
    itemSection.removeChild(itemToRemove);
}

// collect form
function collectFormData() {
    const items = itemsList.map(item => {
        const productSelect = item.querySelector('select');
        const usageDateInput = item.querySelector('input[name^="usage-date"]');
        const amountInput = item.querySelector('input[name^="amount"]');

        return {
            product: productSelect.value,  // product id
            usageDate: usageDateInput.value,
            amount: amountInput.value
        };
    });

    return { items }; // return object
}

// form submission
async function handleSubmit(event) {
    event.preventDefault();  // stop default behavior
    
    const formData = collectFormData();  // get data
    
    try {
        const response = await fetch('/api/usage-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const responseData = await response.json(); // get response

        // check status
        if (response.ok && responseData.status === 200) {
            // reset form
            resetForm();

            // successful response
            alert("Form submitted successfully!");
        } else {
            alert("Failed to submit the form. Please try again.");
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        alert("An error occurred. Please try again.");
    }
}


// reset form
async function resetForm() {
    // clear elements
    const productSelects = document.querySelectorAll('select');
    productSelects.forEach(select => {
        select.selectedIndex = 0; // default
    });

    // clear dates
    const inputs = document.querySelectorAll('input[type="date"], input[name^="amount"]');
    inputs.forEach(input => {
        input.value = '';
    });

    // clear items
    itemsList = [];
    const itemSection = document.getElementById('items-section');
    itemSection.innerHTML = '';

    // add product options
    const products = await fetchProducts();
    addItem(products);
}

// listen for submit
document.getElementById('submit-btn').addEventListener('click', handleSubmit);

// init on page load
window.onload = init;
