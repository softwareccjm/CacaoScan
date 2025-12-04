// vitest.config.js
import { defineConfig } from "file:///C:/Documentos/trabajos/Programing/proyecyto%20de%20cacao/Proyecto_Git/cacaoscan/frontend/node_modules/.pnpm/vitest@2.1.9_@types+node@24_9713af0187d3ac59320960856d077ced/node_modules/vitest/dist/config.js";
import vue from "file:///C:/Documentos/trabajos/Programing/proyecyto%20de%20cacao/Proyecto_Git/cacaoscan/frontend/node_modules/.pnpm/@vitejs+plugin-vue@6.0.1_vi_6720c27b958556f68fb43f491c00cc55/node_modules/@vitejs/plugin-vue/dist/index.js";
import { resolve } from "node:path";
var __vite_injected_original_dirname = "C:\\Documentos\\trabajos\\Programing\\proyecyto de cacao\\Proyecto_Git\\cacaoscan\\frontend";
var vitest_config_default = defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.js"],
    threads: true,
    maxThreads: 2,
    minThreads: 1,
    isolate: true,
    testTimeout: 2e4,
    hookTimeout: 2e4,
    sequence: {
      shuffle: false
    },
    exclude: [
      "node_modules",
      "dist",
      "coverage",
      "cypress",
      "**/cypress/**",
      "**/*.cy.js"
    ],
    include: ["src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
    css: {
      modules: {
        classNameStrategy: "non-scoped"
      }
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "lcov"],
      reportsDirectory: "./coverage",
      include: ["src/**"],
      exclude: [
        "node_modules/",
        "src/test/",
        "**/*.d.ts",
        "src/env.d.ts",
        "**/*.config.js",
        "**/*.config.ts",
        "cypress/**",
        "**/cypress/**",
        "**/*.cy.js",
        "dist/",
        "coverage/",
        "src/App.vue",
        "src/main.js",
        "src/components/common/BaseFormField.example.vue",
        "src/services/api/index.js"
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  resolve: {
    alias: {
      "@": resolve(__vite_injected_original_dirname, "./src")
    }
  },
  define: {
    "import.meta.vitest": "undefined"
  }
});
export {
  vitest_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZXN0LmNvbmZpZy5qcyJdLAogICJzb3VyY2VzQ29udGVudCI6IFsiY29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2Rpcm5hbWUgPSBcIkM6XFxcXERvY3VtZW50b3NcXFxcdHJhYmFqb3NcXFxcUHJvZ3JhbWluZ1xcXFxwcm95ZWN5dG8gZGUgY2FjYW9cXFxcUHJveWVjdG9fR2l0XFxcXGNhY2Fvc2NhblxcXFxmcm9udGVuZFwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiQzpcXFxcRG9jdW1lbnRvc1xcXFx0cmFiYWpvc1xcXFxQcm9ncmFtaW5nXFxcXHByb3llY3l0byBkZSBjYWNhb1xcXFxQcm95ZWN0b19HaXRcXFxcY2FjYW9zY2FuXFxcXGZyb250ZW5kXFxcXHZpdGVzdC5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL0M6L0RvY3VtZW50b3MvdHJhYmFqb3MvUHJvZ3JhbWluZy9wcm95ZWN5dG8lMjBkZSUyMGNhY2FvL1Byb3llY3RvX0dpdC9jYWNhb3NjYW4vZnJvbnRlbmQvdml0ZXN0LmNvbmZpZy5qc1wiO2ltcG9ydCB7IGRlZmluZUNvbmZpZyB9IGZyb20gJ3ZpdGVzdC9jb25maWcnXG5pbXBvcnQgdnVlIGZyb20gJ0B2aXRlanMvcGx1Z2luLXZ1ZSdcbmltcG9ydCB7IHJlc29sdmUgfSBmcm9tICdub2RlOnBhdGgnXG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gIHBsdWdpbnM6IFt2dWUoKV0sXG4gIHRlc3Q6IHtcbiAgICBnbG9iYWxzOiB0cnVlLFxuICAgIGVudmlyb25tZW50OiAnanNkb20nLFxuICAgIHNldHVwRmlsZXM6IFsnLi9zcmMvdGVzdC9zZXR1cC5qcyddLFxuICAgIHRocmVhZHM6IHRydWUsXG4gICAgbWF4VGhyZWFkczogMixcbiAgICBtaW5UaHJlYWRzOiAxLFxuICAgIGlzb2xhdGU6IHRydWUsXG4gICAgdGVzdFRpbWVvdXQ6IDIwMDAwLFxuICAgIGhvb2tUaW1lb3V0OiAyMDAwMCxcbiAgICBzZXF1ZW5jZToge1xuICAgICAgc2h1ZmZsZTogZmFsc2VcbiAgICB9LFxuICAgIGV4Y2x1ZGU6IFtcbiAgICAgICdub2RlX21vZHVsZXMnLFxuICAgICAgJ2Rpc3QnLFxuICAgICAgJ2NvdmVyYWdlJyxcbiAgICAgICdjeXByZXNzJyxcbiAgICAgICcqKi9jeXByZXNzLyoqJyxcbiAgICAgICcqKi8qLmN5LmpzJ1xuICAgIF0sXG4gICAgaW5jbHVkZTogWydzcmMvKiovKi57dGVzdCxzcGVjfS57anMsbWpzLGNqcyx0cyxtdHMsY3RzLGpzeCx0c3h9J10sXG4gICAgY3NzOiB7XG4gICAgICBtb2R1bGVzOiB7XG4gICAgICAgIGNsYXNzTmFtZVN0cmF0ZWd5OiAnbm9uLXNjb3BlZCdcbiAgICAgIH1cbiAgICB9LFxuICAgIGNvdmVyYWdlOiB7XG4gICAgICBwcm92aWRlcjogJ3Y4JyxcbiAgICAgIHJlcG9ydGVyOiBbJ3RleHQnLCAnanNvbicsICdsY292J10sXG4gICAgICByZXBvcnRzRGlyZWN0b3J5OiAnLi9jb3ZlcmFnZScsXG4gICAgICBpbmNsdWRlOiBbJ3NyYy8qKiddLFxuICAgICAgZXhjbHVkZTogW1xuICAgICAgICAnbm9kZV9tb2R1bGVzLycsXG4gICAgICAgICdzcmMvdGVzdC8nLFxuICAgICAgICAnKiovKi5kLnRzJyxcbiAgICAgICAgJ3NyYy9lbnYuZC50cycsXG4gICAgICAgICcqKi8qLmNvbmZpZy5qcycsXG4gICAgICAgICcqKi8qLmNvbmZpZy50cycsXG4gICAgICAgICdjeXByZXNzLyoqJyxcbiAgICAgICAgJyoqL2N5cHJlc3MvKionLFxuICAgICAgICAnKiovKi5jeS5qcycsXG4gICAgICAgICdkaXN0LycsXG4gICAgICAgICdjb3ZlcmFnZS8nLFxuICAgICAgICAnc3JjL0FwcC52dWUnLFxuICAgICAgICAnc3JjL21haW4uanMnLFxuICAgICAgICAnc3JjL2NvbXBvbmVudHMvY29tbW9uL0Jhc2VGb3JtRmllbGQuZXhhbXBsZS52dWUnLFxuICAgICAgICAnc3JjL3NlcnZpY2VzL2FwaS9pbmRleC5qcydcbiAgICAgIF0sXG4gICAgICB0aHJlc2hvbGRzOiB7XG4gICAgICAgIGdsb2JhbDoge1xuICAgICAgICAgIGJyYW5jaGVzOiA4MCxcbiAgICAgICAgICBmdW5jdGlvbnM6IDgwLFxuICAgICAgICAgIGxpbmVzOiA4MCxcbiAgICAgICAgICBzdGF0ZW1lbnRzOiA4MFxuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICB9LFxuICByZXNvbHZlOiB7XG4gICAgYWxpYXM6IHtcbiAgICAgICdAJzogcmVzb2x2ZShfX2Rpcm5hbWUsICcuL3NyYycpXG4gICAgfVxuICB9LFxuICBkZWZpbmU6IHtcbiAgICAnaW1wb3J0Lm1ldGEudml0ZXN0JzogJ3VuZGVmaW5lZCdcbiAgfVxufSlcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBc2MsU0FBUyxvQkFBb0I7QUFDbmUsT0FBTyxTQUFTO0FBQ2hCLFNBQVMsZUFBZTtBQUZ4QixJQUFNLG1DQUFtQztBQUl6QyxJQUFPLHdCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTLENBQUMsSUFBSSxDQUFDO0FBQUEsRUFDZixNQUFNO0FBQUEsSUFDSixTQUFTO0FBQUEsSUFDVCxhQUFhO0FBQUEsSUFDYixZQUFZLENBQUMscUJBQXFCO0FBQUEsSUFDbEMsU0FBUztBQUFBLElBQ1QsWUFBWTtBQUFBLElBQ1osWUFBWTtBQUFBLElBQ1osU0FBUztBQUFBLElBQ1QsYUFBYTtBQUFBLElBQ2IsYUFBYTtBQUFBLElBQ2IsVUFBVTtBQUFBLE1BQ1IsU0FBUztBQUFBLElBQ1g7QUFBQSxJQUNBLFNBQVM7QUFBQSxNQUNQO0FBQUEsTUFDQTtBQUFBLE1BQ0E7QUFBQSxNQUNBO0FBQUEsTUFDQTtBQUFBLE1BQ0E7QUFBQSxJQUNGO0FBQUEsSUFDQSxTQUFTLENBQUMsc0RBQXNEO0FBQUEsSUFDaEUsS0FBSztBQUFBLE1BQ0gsU0FBUztBQUFBLFFBQ1AsbUJBQW1CO0FBQUEsTUFDckI7QUFBQSxJQUNGO0FBQUEsSUFDQSxVQUFVO0FBQUEsTUFDUixVQUFVO0FBQUEsTUFDVixVQUFVLENBQUMsUUFBUSxRQUFRLE1BQU07QUFBQSxNQUNqQyxrQkFBa0I7QUFBQSxNQUNsQixTQUFTLENBQUMsUUFBUTtBQUFBLE1BQ2xCLFNBQVM7QUFBQSxRQUNQO0FBQUEsUUFDQTtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBLFFBQ0E7QUFBQSxNQUNGO0FBQUEsTUFDQSxZQUFZO0FBQUEsUUFDVixRQUFRO0FBQUEsVUFDTixVQUFVO0FBQUEsVUFDVixXQUFXO0FBQUEsVUFDWCxPQUFPO0FBQUEsVUFDUCxZQUFZO0FBQUEsUUFDZDtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxRQUFRLGtDQUFXLE9BQU87QUFBQSxJQUNqQztBQUFBLEVBQ0Y7QUFBQSxFQUNBLFFBQVE7QUFBQSxJQUNOLHNCQUFzQjtBQUFBLEVBQ3hCO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K
