/**
 * Virtual Scrolling Component for REDLINE Web GUI
 * Provides high-performance scrolling for large datasets
 */

class VirtualScrollTable {
    constructor(container, options = {}) {
        this.container = $(container);
        this.options = {
            rowHeight: 30,
            visibleRows: 20,
            buffer: 5,
            ...options
        };
        
        this.data = [];
        this.columns = [];
        this.currentPage = 1;
        this.pageSize = 100;
        this.totalRows = 0;
        this.isLoading = false;
        
        this.scrollTop = 0;
        this.startIndex = 0;
        this.endIndex = 0;
        
        this.init();
    }
    
    init() {
        this.createStructure();
        this.bindEvents();
        this.render();
    }
    
    createStructure() {
        // Create virtual scroll container
        const html = `
            <div class="virtual-scroll-container">
                <div class="virtual-scroll-header">
                    <div class="virtual-scroll-pagination">
                        <button class="btn btn-sm btn-outline-primary" id="prevPageBtn" disabled>
                            <i class="fas fa-chevron-left"></i> Previous
                        </button>
                        <span class="pagination-info">
                            Page <span id="currentPage">1</span> of <span id="totalPages">1</span>
                            (<span id="totalRows">0</span> rows)
                        </span>
                        <button class="btn btn-sm btn-outline-primary" id="nextPageBtn" disabled>
                            Next <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                    <div class="virtual-scroll-controls">
                        <label class="form-label">Rows per page:</label>
                        <select class="form-select form-select-sm" id="pageSizeSelect" style="width: auto;">
                            <option value="50">50</option>
                            <option value="100" selected>100</option>
                            <option value="200">200</option>
                            <option value="500">500</option>
                        </select>
                    </div>
                </div>
                <div class="virtual-scroll-viewport">
                    <div class="virtual-scroll-content">
                        <table class="table table-striped table-hover virtual-table">
                            <thead class="table-dark">
                                <tr id="virtualTableHeader"></tr>
                            </thead>
                            <tbody id="virtualTableBody"></tbody>
                        </table>
                    </div>
                    <div class="virtual-scroll-loading" id="loadingIndicator" style="display: none;">
                        <div class="spinner-border spinner-border-sm" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <span class="ms-2">Loading data...</span>
                    </div>
                </div>
                <div class="virtual-scroll-footer">
                    <div class="row-count">
                        Showing <span id="showingStart">0</span> to <span id="showingEnd">0</span> of <span id="showingTotal">0</span> entries
                    </div>
                    <div class="performance-stats">
                        <small class="text-muted">
                            Render time: <span id="renderTime">0</span>ms | 
                            Memory usage: <span id="memoryUsage">0</span>MB
                        </small>
                    </div>
                </div>
            </div>
        `;
        
        this.container.html(html);
        
        // Cache jQuery elements
        this.elements = {
            viewport: this.container.find('.virtual-scroll-viewport'),
            content: this.container.find('.virtual-scroll-content'),
            table: this.container.find('.virtual-table'),
            header: this.container.find('#virtualTableHeader'),
            body: this.container.find('#virtualTableBody'),
            loadingIndicator: this.container.find('#loadingIndicator'),
            prevBtn: this.container.find('#prevPageBtn'),
            nextBtn: this.container.find('#nextPageBtn'),
            currentPageSpan: this.container.find('#currentPage'),
            totalPagesSpan: this.container.find('#totalPages'),
            totalRowsSpan: this.container.find('#totalRows'),
            pageSizeSelect: this.container.find('#pageSizeSelect'),
            showingStart: this.container.find('#showingStart'),
            showingEnd: this.container.find('#showingEnd'),
            showingTotal: this.container.find('#showingTotal'),
            renderTime: this.container.find('#renderTime'),
            memoryUsage: this.container.find('#memoryUsage')
        };
    }
    
    bindEvents() {
        // Pagination controls
        this.elements.prevBtn.on('click', () => this.previousPage());
        this.elements.nextBtn.on('click', () => this.nextPage());
        this.elements.pageSizeSelect.on('change', (e) => {
            this.pageSize = parseInt(e.target.value);
            this.currentPage = 1;
            this.loadData();
        });
        
        // Scroll events for virtual scrolling
        this.elements.viewport.on('scroll', () => this.handleScroll());
        
        // Window resize
        $(window).on('resize', () => this.updateVisibleRows());
    }
    
    setData(data, columns) {
        this.data = data;
        this.columns = columns;
        this.totalRows = data.length;
        this.currentPage = 1;
        this.updatePagination();
        this.render();
    }
    
    async loadDataFromAPI(url, params = {}) {
        if (this.isLoading) return;
        
        this.showLoading();
        
        try {
            const startTime = performance.now();
            
            // Add pagination parameters
            const requestParams = {
                page: this.currentPage,
                per_page: this.pageSize,
                ...params
            };
            
            const response = await $.ajax({
                url: url,
                method: 'GET',
                data: requestParams,
                dataType: 'json'
            });
            
            if (response.error) {
                throw new Error(response.error);
            }
            
            this.data = response.preview || response.data || [];
            this.columns = response.columns || [];
            this.totalRows = response.total_rows || response.pagination?.total || 0;
            
            this.updatePagination();
            this.render();
            
            const endTime = performance.now();
            this.updatePerformanceStats(endTime - startTime);
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load data: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    updatePagination() {
        const totalPages = Math.ceil(this.totalRows / this.pageSize);
        
        this.elements.currentPageSpan.text(this.currentPage);
        this.elements.totalPagesSpan.text(totalPages);
        this.elements.totalRowsSpan.text(this.totalRows.toLocaleString());
        
        this.elements.prevBtn.prop('disabled', this.currentPage <= 1);
        this.elements.nextBtn.prop('disabled', this.currentPage >= totalPages);
        
        // Update showing info
        const start = (this.currentPage - 1) * this.pageSize + 1;
        const end = Math.min(this.currentPage * this.pageSize, this.totalRows);
        
        this.elements.showingStart.text(start.toLocaleString());
        this.elements.showingEnd.text(end.toLocaleString());
        this.elements.showingTotal.text(this.totalRows.toLocaleString());
    }
    
    render() {
        const startTime = performance.now();
        
        // Render header
        this.renderHeader();
        
        // Render body
        this.renderBody();
        
        const endTime = performance.now();
        this.updatePerformanceStats(endTime - startTime);
    }
    
    renderHeader() {
        const headerHtml = this.columns.map(col => 
            `<th class="text-nowrap">${col}</th>`
        ).join('');
        
        this.elements.header.html(headerHtml);
    }
    
    renderBody() {
        if (!this.data || this.data.length === 0) {
            this.elements.body.html(`
                <tr>
                    <td colspan="${this.columns.length}" class="text-center text-muted py-4">
                        No data available
                    </td>
                </tr>
            `);
            return;
        }
        
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = Math.min(startIndex + this.pageSize, this.data.length);
        const pageData = this.data.slice(startIndex, endIndex);
        
        const bodyHtml = pageData.map((row, index) => {
            const rowHtml = this.columns.map(col => {
                let value = row[col];
                
                // Format value based on type
                if (value === null || value === undefined) {
                    value = '<span class="text-muted">-</span>';
                } else if (typeof value === 'number') {
                    value = value.toLocaleString();
                } else if (typeof value === 'string' && value.length > 50) {
                    value = `<span title="${value}">${value.substring(0, 50)}...</span>`;
                } else {
                    value = String(value);
                }
                
                return `<td class="text-nowrap">${value}</td>`;
            }).join('');
            
            return `<tr data-index="${startIndex + index}">${rowHtml}</tr>`;
        }).join('');
        
        this.elements.body.html(bodyHtml);
    }
    
    handleScroll() {
        // This method can be extended for true virtual scrolling
        // For now, we're using pagination-based approach
    }
    
    updateVisibleRows() {
        const viewportHeight = this.elements.viewport.height();
        this.options.visibleRows = Math.floor(viewportHeight / this.options.rowHeight);
    }
    
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadData();
        }
    }
    
    nextPage() {
        const totalPages = Math.ceil(this.totalRows / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.loadData();
        }
    }
    
    loadData() {
        // This method should be overridden by the parent component
        // to load data from the API
        this.render();
    }
    
    showLoading() {
        this.isLoading = true;
        this.elements.loadingIndicator.show();
    }
    
    hideLoading() {
        this.isLoading = false;
        this.elements.loadingIndicator.hide();
    }
    
    showError(message) {
        this.elements.body.html(`
            <tr>
                <td colspan="${this.columns.length}" class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${message}
                </td>
            </tr>
        `);
    }
    
    updatePerformanceStats(renderTime) {
        this.elements.renderTime.text(Math.round(renderTime));
        
        // Estimate memory usage
        const memoryUsage = (this.data.length * this.columns.length * 50) / (1024 * 1024); // Rough estimate
        this.elements.memoryUsage.text(memoryUsage.toFixed(1));
    }
    
    // Public API methods
    refresh() {
        this.currentPage = 1;
        this.loadData();
    }
    
    getCurrentPage() {
        return this.currentPage;
    }
    
    getPageSize() {
        return this.pageSize;
    }
    
    getTotalRows() {
        return this.totalRows;
    }
    
    destroy() {
        this.container.empty();
        $(window).off('resize');
    }
}

// Make VirtualScrollTable available globally
window.VirtualScrollTable = VirtualScrollTable;
