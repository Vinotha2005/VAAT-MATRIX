/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Georgia', 'Times New Roman', 'serif'],
      },
      boxShadow: {
        soft: '0 12px 40px rgba(15, 23, 42, 0.12)',
      },
    },
  },
  plugins: [],
}
