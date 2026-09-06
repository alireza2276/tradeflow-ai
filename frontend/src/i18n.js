import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'


const resources = {
  fa: {
    translation: {
      common: {
        appName: 'TradeFlowAI',
        tradeFinance: 'مدیریت تأمین مالی تجارت',
        loading: 'در حال بارگذاری...',
        save: 'ذخیره',
        cancel: 'انصراف',
        edit: 'ویرایش',
        delete: 'حذف',
        search: 'جستجو',
        exportCsv: 'خروجی CSV',
        active: 'فعال',
        inactive: 'غیرفعال',
        logout: 'خروج',
        persian: 'فارسی',
        english: 'English',
      },

      navigation: {
        dashboard: 'داشبورد',
        companies: 'شرکت‌ها',
        registrationOrders: 'ثبت سفارش‌ها',
        paymentInstruments: 'ابزار پرداخت',
        currencyPurchases: 'خریدهای ارز',
        shipmentParts: 'اسناد حمل',
        invoices: 'صورتحساب‌ها',
        notifications: 'اعلان‌ها',
      },

      registrationOrders: {
        title: 'ثبت سفارش‌ها',
        description:
          'مدیریت ثبت سفارش‌های تجاری و تخصیص ارز آن‌ها',
        addOrder: 'افزودن ثبت سفارش',
        orderNumber: 'شماره ثبت سفارش',
        company: 'شرکت',
        registeredAmount: 'مبلغ ثبت‌شده',
        currency: 'ارز',
        status: 'وضعیت',
        sort: 'مرتب‌سازی ثبت سفارش‌ها',
        actions: 'عملیات',
        searchPlaceholder:
          'جستجو بر اساس ثبت سفارش، شرکت، شناسه ملی یا ارز...',
        allCurrencies: 'همه ارزها',
        allStatuses: 'همه وضعیت‌ها',
        newestFirst: 'جدیدترین',
        oldestFirst: 'قدیمی‌ترین',
        amountHighToLow: 'مبلغ: زیاد به کم',
        amountLowToHigh: 'مبلغ: کم به زیاد',
        orderNumberAsc: 'شماره ثبت سفارش: صعودی',
        orderNumberDesc: 'شماره ثبت سفارش: نزولی',
        empty:
          'ثبت سفارشی مطابق جستجو یا فیلترهای فعلی پیدا نشد.',
        loadingTitle:
          'در حال بارگذاری ثبت سفارش‌ها',
        loadingDescription:
          'اطلاعات ثبت سفارش‌ها در حال دریافت است.',
        loadError:
          'بارگذاری ثبت سفارش‌ها انجام نشد.',
        exporting:
          'در حال تهیه خروجی...',
      },
    },
  },

  en: {
    translation: {
      common: {
        appName: 'TradeFlowAI',
        tradeFinance: 'Trade Finance Management',
        loading: 'Loading...',
        save: 'Save',
        cancel: 'Cancel',
        edit: 'Edit',
        delete: 'Delete',
        search: 'Search',
        exportCsv: 'Export CSV',
        active: 'Active',
        inactive: 'Inactive',
        logout: 'Logout',
        persian: 'فارسی',
        english: 'English',
      },

      navigation: {
        dashboard: 'Dashboard',
        companies: 'Companies',
        registrationOrders: 'Registration Orders',
        paymentInstruments: 'Payment Instruments',
        currencyPurchases: 'Currency Purchases',
        shipmentParts: 'Shipment Parts',
        invoices: 'Invoices',
        notifications: 'Notifications',
      },

      registrationOrders: {
        title: 'Registration Orders',
        description:
          'Manage registered trade orders and their currency allocations.',
        addOrder: 'Add Order',
        orderNumber: 'Order Number',
        company: 'Company',
        registeredAmount: 'Registered Amount',
        currency: 'Currency',
        status: 'Status',
        sort: 'Sort registration orders',
        actions: 'Actions',
        searchPlaceholder:
          'Search order, company, national ID or currency...',
        allCurrencies: 'All Currencies',
        allStatuses: 'All Statuses',
        newestFirst: 'Newest First',
        oldestFirst: 'Oldest First',
        amountHighToLow: 'Amount: High to Low',
        amountLowToHigh: 'Amount: Low to High',
        orderNumberAsc: 'Order Number: A-Z',
        orderNumberDesc: 'Order Number: Z-A',
        empty:
          'No registration orders match the current search or filters.',
        loadingTitle:
          'Loading registration orders',
        loadingDescription:
          'Fetching trade registration orders.',
        loadError:
          'Unable to load registration orders',
        exporting:
          'Exporting...',
      },
    },
  },
}


i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'fa',
    fallbackLng: 'en',

    interpolation: {
      escapeValue: false,
    },
  })


export default i18n