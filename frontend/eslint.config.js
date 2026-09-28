import { defineConfig } from 'eslint/config'
import pluginVue from 'eslint-plugin-vue'
import pluginJs from "@eslint/js";
import globals from 'globals'

export default defineConfig([
// 1. These rules are used for Javascript file only
  {
    files: ['src/**/*.{js,mjs,cjs,vue}'],
    extends: [pluginJs.configs.recommended],
     languageOptions: {
      globals: {
        ...globals.browser
      }
    }
  },
// 2. These rules are used for .vue specific files
  {
    files: ['src/**/*.vue'],
    extends: [pluginVue.configs['flat/strongly-recommended']]
  }
])