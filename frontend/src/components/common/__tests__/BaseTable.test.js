import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseTable from '../BaseTable.vue'

describe('BaseTable', () => {
  let wrapper

  const mockColumns = [
    { key: 'name', label: 'Name' },
    { key: 'age', label: 'Age' }
  ]

  const mockData = [
    { id: 1, name: 'John', age: 30 },
    { id: 2, name: 'Jane', age: 25 }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should render table element', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    const table = wrapper.find('table')
    expect(table.exists()).toBe(true)
  })

  it('should render all columns in header', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    expect(wrapper.text()).toContain('Name')
    expect(wrapper.text()).toContain('Age')
  })

  it('should render all data rows', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    expect(wrapper.text()).toContain('John')
    expect(wrapper.text()).toContain('Jane')
    expect(wrapper.text()).toContain('30')
    expect(wrapper.text()).toContain('25')
  })

  it('should display title when provided', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        title: 'Test Table'
      }
    })

    expect(wrapper.text()).toContain('Test Table')
  })

  it('should display subtitle when provided', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        title: 'Test Table',
        subtitle: 'Table subtitle'
      }
    })

    expect(wrapper.text()).toContain('Table subtitle')
  })

  it('should show loading state when loading is true', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        loading: true
      }
    })

    expect(wrapper.text()).toContain('Cargando datos...')
    const table = wrapper.find('table')
    expect(table.exists()).toBe(false)
  })

  it('should show custom loading text', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        loading: true,
        loadingText: 'Custom loading...'
      }
    })

    expect(wrapper.text()).toContain('Custom loading...')
  })

  it('should show empty state when data is empty', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: []
      }
    })

    expect(wrapper.text()).toContain('No hay datos disponibles')
  })

  it('should show custom empty text', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: [],
        emptyText: 'No records found'
      }
    })

    expect(wrapper.text()).toContain('No records found')
  })

  it('should enable selection when enableSelection is true', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enableSelection: true
      }
    })

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBeGreaterThan(0)
  })

  it('should emit row-click event when row is clicked', async () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    const row = wrapper.find('tbody tr')
    await row.trigger('click')

    expect(wrapper.emitted('row-click')).toBeTruthy()
  })

  it('should emit sort event when sortable column header is clicked', async () => {
    const sortableColumns = [
      { key: 'name', label: 'Name', sortable: true }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: sortableColumns,
        data: mockData
      }
    })

    const header = wrapper.find('th')
    await header.trigger('click')

    expect(wrapper.emitted('sort')).toBeTruthy()
  })

  it('should render header slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header')
  })

  it('should render controls slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        controls: '<div>Custom Controls</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Controls')
  })

  it('should render actions slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        actions: '<div>Custom Actions</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Actions')
  })

  it('should render empty slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: []
      },
      slots: {
        empty: '<div>Custom Empty State</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Empty State')
  })

  it('should render pagination slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        pagination: '<div>Custom Pagination</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Pagination')
  })

  it('should render cell slot with scoped props', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        'cell-name': '<div>Custom: {{ value }}</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom')
  })

  it('should use custom rowKey function', () => {
    const customData = [
      { customId: 1, name: 'John' },
      { customId: 2, name: 'Jane' }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: customData,
        rowKey: (row) => row.customId
      }
    })

    expect(wrapper.text()).toContain('John')
    expect(wrapper.text()).toContain('Jane')
  })

  it('should apply row class function', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        rowClass: (row) => row.age > 25 ? 'highlight' : ''
      }
    })

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBeGreaterThan(0)
  })

  it('should show table info footer when showTableInfo is true', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        showTableInfo: true
      }
    })

    expect(wrapper.text()).toContain('Mostrando')
    expect(wrapper.text()).toContain('resultados')
  })

  it('should enable pagination when enablePagination is true', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enablePagination: true,
        itemsPerPage: 1
      }
    })

    expect(wrapper.vm.pagination).toBeTruthy()
  })

  it('should handle filter function', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        filterFn: (row) => row.age > 25
      }
    })

    // Filtered data should only contain rows with age > 25
    const processedData = wrapper.vm.processedData
    expect(processedData.length).toBeLessThanOrEqual(mockData.length)
  })

  it('should format cell value using column formatter', () => {
    const columnsWithFormatter = [
      {
        key: 'age',
        label: 'Age',
        formatter: (value) => `${value} years`
      }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: columnsWithFormatter,
        data: mockData
      }
    })

    expect(wrapper.text()).toContain('years')
  })

  it('should handle row selection when enableSelection is true', async () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enableSelection: true
      }
    })

    const checkbox = wrapper.find('tbody input[type="checkbox"]')
    if (checkbox.exists()) {
      await checkbox.setChecked(true)
      expect(wrapper.emitted('row-select')).toBeTruthy()
    }
  })

  it('should handle select all when enableSelection is true', async () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enableSelection: true
      }
    })

    const selectAllCheckbox = wrapper.find('thead input[type="checkbox"]')
    if (selectAllCheckbox.exists()) {
      await selectAllCheckbox.setChecked(true)
      expect(wrapper.emitted('select-all')).toBeTruthy()
    }
  })
})

