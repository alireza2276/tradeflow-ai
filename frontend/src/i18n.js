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
        close: 'بستن',
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

      dashboard: {
        title: 'داشبورد',
        description:
          'پایش عملیات ارزی و سررسیدهای مربوط به ارائه اسناد حمل',

        loadingTitle:
          'در حال بارگذاری داشبورد',
        loadingDescription:
          'آخرین اطلاعات عملیات ارزی در حال دریافت است.',
        loadError:
          'بارگذاری داشبورد انجام نشد.',

        activeOrders: 'ثبت سفارش‌های فعال',
        activeOrdersSubtitle:
          'ثبت سفارش‌هایی که در حال حاضر فعال هستند',

        activePurchases: 'خریدهای ارز فعال',
        activePurchasesSubtitle:
          'خریدهای ارزی که در حال پایش هستند',

        dueSoon: 'نزدیک به سررسید',
        dueSoonSubtitle:
          'سررسیدهای ۳۰ روز آینده',

        overdue: 'سررسید گذشته',
        overdueSubtitle:
          'پرونده‌هایی که نیازمند پیگیری فوری هستند',

        currencyExposure: 'وضعیت ارزی',
        currencyExposureDescription:
          'مبالغ خریداری‌شده، مستندشده و باقی‌مانده به تفکیک ارز',
        noCurrencyData:
          'اطلاعاتی از خرید ارز برای نمایش وجود ندارد.',

        attentionTitle:
          'پرونده‌های نیازمند پیگیری',
        attentionDescription:
          'خریدهای ارزی سررسید گذشته یا نزدیک به مهلت ارائه اسناد حمل',
      },

      currencyCard: {
        currency: 'ارز',
        remainingAmount: 'مبلغ باقی‌مانده',
        purchased: 'خریداری‌شده',
        documented: 'مستندشده',
      },

      attentionTable: {
        company: 'شرکت',
        order: 'ثبت سفارش',
        currency: 'ارز',
        remaining: 'باقی‌مانده',
        deadline: 'سررسید',
        status: 'وضعیت',

        empty:
          'در حال حاضر پرونده‌ای نیازمند پیگیری نیست.',

        overdue: 'سررسید گذشته',
        dueSoon: 'نزدیک به سررسید',

        daysOverdue:
          '{{count}} روز از سررسید گذشته است',
        dueToday:
          'سررسید امروز است',
        daysLeft:
          '{{count}} روز تا سررسید باقی مانده است',
      },

      companies: {
        title: 'شرکت‌ها',
        description:
          'مدیریت شرکت‌های مرتبط با عملیات ارزی و تجاری',

        addCompany:
          'افزودن شرکت',

        company:
          'شرکت',

        nationalId:
          'شناسه ملی',

        companyType:
          'نوع شرکت',

        commercial:
          'بازرگانی',

        production:
          'تولیدی',

        actions:
          'عملیات',

        empty:
          'هنوز شرکتی ثبت نشده است.',

        loadingTitle:
          'در حال بارگذاری شرکت‌ها',

        loadingDescription:
          'اطلاعات شرکت‌ها در حال دریافت است.',

        loadError:
          'بارگذاری شرکت‌ها انجام نشد.',

        deleting:
          'در حال حذف...',

        deleteConfirmation:
          'آیا از حذف شرکت «{{name}}» مطمئن هستید؟ این عملیات قابل بازگشت نیست.',
      },

      companyForm: {
        addTitle:
          'افزودن شرکت',

        editTitle:
          'ویرایش شرکت',

        addDescription:
          'ثبت شرکت جدید در TradeFlowAI',

        editDescription:
          'اطلاعات شرکت را ویرایش کنید.',

        companyName:
          'نام شرکت',

        companyNamePlaceholder:
          'نام شرکت را وارد کنید',

        nationalId:
          'شناسه ملی',

        nationalIdPlaceholder:
          'شناسه ملی را وارد کنید',

        companyType:
          'نوع شرکت',

        commercial:
          'بازرگانی',

        production:
          'تولیدی',

        saveChanges:
          'ذخیره تغییرات',

        createCompany:
          'ایجاد شرکت',

        saving:
          'در حال ذخیره...',

        creating:
          'در حال ایجاد...',
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
        close: 'Close',
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

      dashboard: {
        title: 'Dashboard',
        description:
          'Monitor trade finance operations and compliance deadlines.',

        loadingTitle:
          'Loading dashboard',
        loadingDescription:
          'Fetching the latest trade finance data.',
        loadError:
          'Unable to load dashboard',

        activeOrders: 'Active Orders',
        activeOrdersSubtitle:
          'Registration orders currently active',

        activePurchases: 'Active Purchases',
        activePurchasesSubtitle:
          'Currency purchases under monitoring',

        dueSoon: 'Due Soon',
        dueSoonSubtitle:
          'Deadlines within the next 30 days',

        overdue: 'Overdue',
        overdueSubtitle:
          'Cases requiring immediate attention',

        currencyExposure: 'Currency Exposure',
        currencyExposureDescription:
          'Purchased, documented, and remaining amounts by currency.',
        noCurrencyData:
          'No currency purchase data available.',

        attentionTitle:
          'Cases Requiring Attention',
        attentionDescription:
          'Purchases that are overdue or approaching their compliance deadline.',
      },

      currencyCard: {
        currency: 'Currency',
        remainingAmount: 'Remaining Amount',
        purchased: 'Purchased',
        documented: 'Documented',
      },

      attentionTable: {
        company: 'Company',
        order: 'Order',
        currency: 'Currency',
        remaining: 'Remaining',
        deadline: 'Deadline',
        status: 'Status',

        empty:
          'No cases currently require attention.',

        overdue: 'Overdue',
        dueSoon: 'Due Soon',

        daysOverdue:
          '{{count}} days overdue',
        dueToday:
          'Due today',
        daysLeft:
          '{{count}} days left',
      },

      companies: {
        title: 'Companies',
        description:
          'Manage companies involved in trade finance operations.',

        addCompany:
          'Add Company',

        company:
          'Company',

        nationalId:
          'National ID',

        companyType:
          'Company Type',

        commercial:
          'Commercial',

        production:
          'Production',

        actions:
          'Actions',

        empty:
          'No companies have been registered yet.',

        loadingTitle:
          'Loading companies',

        loadingDescription:
          'Fetching company records from TradeFlowAI.',

        loadError:
          'Unable to load companies',

        deleting:
          'Deleting...',

        deleteConfirmation:
          'Delete "{{name}}"? This action cannot be undone.',
      },

      companyForm: {
        addTitle:
          'Add Company',

        editTitle:
          'Edit Company',

        addDescription:
          'Register a new company in TradeFlowAI.',

        editDescription:
          'Update company information.',

        companyName:
          'Company Name',

        companyNamePlaceholder:
          'Enter company name',

        nationalId:
          'National ID',

        nationalIdPlaceholder:
          'Enter national ID',

        companyType:
          'Company Type',

        commercial:
          'Commercial',

        production:
          'Production',

        saveChanges:
          'Save Changes',

        createCompany:
          'Create Company',

        saving:
          'Saving...',

        creating:
          'Creating...',
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