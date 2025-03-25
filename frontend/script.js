document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM content loaded');
    const productList = document.getElementById('product-list');
    const sortOptions = document.getElementById('sort-options');
    const searchButton = document.getElementById('search-button');
    const searchQuery = document.getElementById('search-query');
    const loadingIndicator = document.getElementById('loading-indicator');
    const sortDiv = document.getElementById('sort');

    function displayProducts(products) {
        console.log('Number of products:', products.length);
        productList.innerHTML = '';
        products.forEach(product => {
            const productDiv = document.createElement('div');
            productDiv.className = 'product';
            productDiv.innerHTML = `
                <div class="product-image">
                    <img src="${product.image_url}" alt="${product.product_name}">
                </div>
                <div class="product-details">
                    <h2>${product.product_name}</h2>
                    <p>Price: ₹${product.price}</p>
                    <p>Rating: ${product.avg_rating} (${product.rating_count} reviews)</p>
                    <a href="${product.product_url}" target="_blank">View Product</a>
                    <img class="site-logo" src="${product.logo}" alt="site logo">
                </div>
            `;
            productList.appendChild(productDiv);
        });
        
    }

    function sortProducts(products, criteria) {
        const sortedProducts = [...products].sort((a, b) => {
            if (criteria === 'price') {
                return a[criteria] - b[criteria];
            } else if (criteria === 'avg_rating' || criteria === 'rating_count') {
                return b[criteria] - a[criteria];
            }
        });
        displayProducts(sortedProducts);
    }

    function fetchProducts(query) {
        console.log('Fetching products for query:', query);
        productList.innerHTML = '';
        loadingIndicator.style.display = 'block';
        fetch('http://127.0.0.1:5002/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Received data:', data);
            pollForFile();
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            console.error('Error fetching search results:', error);
        });
    }

    function pollForFile() {
        console.log('Polling for file...');
        fetch('http://127.0.0.1:5002/product_info')
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    throw new Error('File not found');
                }
            })
            .then(text => {
                // console.log('Fetched text:', text); // Debugging line
                const data = text.trim().split('\n').map(JSON.parse);
                loadingIndicator.style.display = 'none';
                
                document.getElementById('sort-container').style.display = 'flex';

                // sortDiv.style.display = 'block';
                displayProducts(data);
                sortProducts(data, sortOptions.value);
                sortOptions.addEventListener('change', (event) => {
                    const criteria = event.target.value;
                    console.log('Sorting by:', criteria);
                    sortProducts(data, criteria);
                });
            })
            .catch(error => {
                console.log('File not found, retrying...'); // Debugging line
                setTimeout(pollForFile, 1000); // Retry after 1 second
            });
    }

    searchButton.addEventListener('click', (event) => {
        // sortDiv.style.display = 'none';
        // event.preventDefault(); // Prevent default form submission
        const query = searchQuery.value;
        console.log('Search button clicked, query:', query);
        if (query) {
            fetchProducts(query);
        }
    });
});