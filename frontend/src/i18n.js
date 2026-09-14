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
        approvals: 'درخواست‌های تأیید',
        auditTrail: 'ردپای حسابرسی',
      },

      auditTrail: {
        title: 'ردپای حسابرسی',
        description: 'ثبت غیرقابل‌تغییر عملیات حساس، تغییرات داده و تصمیم‌های Maker-Checker',
        loading: 'در حال بارگذاری رویدادهای حسابرسی...',
        loadError: 'بارگذاری ردپای حسابرسی انجام نشد.',
        empty: 'هنوز رویداد حسابرسی ثبت نشده است.',
        time: 'زمان',
        actor: 'کاربر',
        action: 'عملیات',
        target: 'نوع رکورد',
        targetId: 'شناسه رکورد',
        reason: 'دلیل',
        details: 'جزئیات',
        showDetails: 'نمایش',
        hideDetails: 'بستن',
        before: 'مقدار قبل',
        after: 'مقدار بعد',
        metadata: 'اطلاعات درخواست',
        system: 'سیستم',
        actions: {
          CREATE: 'ایجاد',
          UPDATE: 'ویرایش',
          VOID: 'ابطال',
          DELETE: 'حذف',
          REQUEST_SUBMITTED: 'ارسال درخواست',
          REQUEST_APPROVED: 'تأیید درخواست',
          REQUEST_REJECTED: 'رد درخواست',
        },
        targets: {
          'companies.company': 'شرکت',
          'trade_orders.registrationorder': 'ثبت سفارش',
          'trade_orders.paymentinstrument': 'ابزار پرداخت',
          'trade_orders.currencypurchase': 'خرید ارز',
          'trade_orders.shipmentpart': 'سند حمل',
          'documents.invoice': 'صورتحساب',
          currency_purchase: 'خرید ارز',
          shipment_part: 'سند حمل',
        },
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

      registrationOrderForm: {
        addTitle: 'افزودن ثبت سفارش',
        editTitle: 'ویرایش ثبت سفارش',

        addDescription:
          'ثبت یک سفارش تجاری جدید',
        editDescription:
          'اطلاعات ثبت سفارش را ویرایش کنید.',

        company: 'شرکت',
        selectCompany: 'انتخاب شرکت',
        loadingCompanies: 'در حال بارگذاری شرکت‌ها...',

        orderNumber: 'شماره ثبت سفارش',
        orderNumberPlaceholder: 'مثال: TF-USD-002',

        registeredAmount: 'مبلغ ثبت‌شده',
        registeredAmountPlaceholder: 'مثال: 50000',

        currency: 'ارز',
        currencyPlaceholder: 'USD',

        activeOrder: 'ثبت سفارش فعال',

        saveChanges: 'ذخیره تغییرات',
        createOrder: 'ایجاد ثبت سفارش',
        saving: 'در حال ذخیره...',
        creating: 'در حال ایجاد...',

        selectCompanyError:
          'لطفاً یک شرکت انتخاب کنید.',

        requiredFieldsError:
          'لطفاً تمام فیلدهای الزامی را تکمیل کنید.',

        invalidAmountError:
          'مبلغ ثبت‌شده باید بیشتر از صفر باشد.',

        invalidCurrencyError:
          'کد ارز باید یک کد معتبر سه‌حرفی باشد.',
      },

      currencyPurchases: {
        title: 'خریدهای ارز',
        description:
          'مدیریت خریدهای ارز و سررسیدهای مرتبط با آن‌ها',

        addPurchase:
          'افزودن خرید ارز',

        company:
          'شرکت',

        orderNumber:
          'شماره ثبت سفارش',

        amount:
          'مبلغ',

        currency:
          'ارز',

        purchaseDate:
          'تاریخ خرید',

        deadline:
          'سررسید',

        actions:
          'عملیات',

        empty:
          'خرید ارزی ثبت نشده است.',

        loading:
          'در حال بارگذاری خریدهای ارز...',

        loadError:
          'بارگذاری خریدهای ارز انجام نشد.',

        requestVoid:
          'درخواست ابطال',

        voidTitle:
          'درخواست ابطال خرید ارز',

        voidDescription:
          'برای ارسال درخواست ابطال، دلیل ابطال را وارد کنید.',

        voidReason:
          'دلیل ابطال',

        voidReasonRequired:
          'وارد کردن دلیل ابطال الزامی است.',

        voidError:
          'ارسال درخواست ابطال ناموفق بود.',

        voidSubmitting:
          'در حال ارسال درخواست...',

        submitVoid:
          'ارسال درخواست ابطال',
      },

      currencyPurchaseForm: {
        addTitle:
          'افزودن خرید ارز',

        editTitle:
          'درخواست اصلاح خرید ارز',

        addDescription:
          'ثبت درخواست خرید ارز جدید',

        editDescription:
          'مبلغ یا تاریخ خرید ارز را اصلاح و برای تأیید ارسال کنید.',

        registrationOrder:
          'ثبت سفارش',

        selectOrder:
          'انتخاب ثبت سفارش',

        loadingOrders:
          'در حال بارگذاری ثبت سفارش‌ها...',

        currency:
          'ارز',

        purchaseAmount:
          'مبلغ خرید',

        purchaseAmountPlaceholder:
          'مثال: 50000',

        purchaseDate:
          'تاریخ خرید',

        correctionReason:
          'دلیل اصلاح',

        correctionReasonPlaceholder:
          'دلیل اصلاح خرید ارز را وارد کنید',

        correctionReasonError:
          'وارد کردن دلیل اصلاح الزامی است.',

        saveChanges:
          'ارسال درخواست اصلاح',

        createPurchase:
          'ارسال درخواست خرید ارز',

        saving:
          'در حال ارسال درخواست اصلاح...',

        creating:
          'در حال ارسال درخواست...',

        selectOrderError:
          'لطفاً یک ثبت سفارش انتخاب کنید.',

        invalidAmountError:
          'مبلغ خرید باید بیشتر از صفر باشد.',

        purchaseDateError:
          'لطفاً تاریخ خرید را انتخاب کنید.',

        currencyUnavailableError:
          'ارز برای ثبت سفارش انتخاب‌شده در دسترس نیست.',
      },

      shipmentParts: {
        title: 'اسناد حمل',
        description:
          'مدیریت تخصیص اسناد حمل مرتبط با خریدهای ارز',

        addShipmentPart:
          'افزودن سند حمل',

        company:
          'شرکت',

        orderNumber:
          'شماره ثبت سفارش',

        reference:
          'شماره مرجع',

        amount:
          'مبلغ',

        currency:
          'ارز',

        shipmentDate:
          'تاریخ حمل',

        receivedDate:
          'تاریخ دریافت',

        notes:
          'یادداشت',

        actions:
          'عملیات',

        empty:
          'سند حملی ثبت نشده است.',

        loading:
          'در حال بارگذاری اسناد حمل...',

        loadError:
          'بارگذاری اطلاعات اسناد حمل انجام نشد.',

        requestVoid:
          'درخواست ابطال',

        voided:
          'باطل‌شده',

        voidTitle:
          'درخواست ابطال سند حمل',

        voidDescription:
          'برای ارسال درخواست ابطال سند حمل، دلیل را وارد کنید.',

        voidReason:
          'دلیل ابطال',

        voidReasonRequired:
          'وارد کردن دلیل ابطال الزامی است.',

        voidError:
          'ارسال درخواست ابطال سند حمل انجام نشد.',

        voidSubmitting:
          'در حال ارسال درخواست...',

        submitVoid:
          'ارسال درخواست ابطال',
        voidReasonPrompt: 'دلیل ابطال سند حمل را وارد کنید:',

      },

      shipmentPartForm: {
        addTitle: 'افزودن سند حمل',
        editTitle: 'درخواست اصلاح سند حمل',
        addDescription: 'ثبت درخواست سند حمل جدید برای یک خرید ارز',
        editDescription: 'اطلاعات سند حمل را اصلاح و برای تأیید ارسال کنید.',
        currencyPurchase: 'خرید ارز',
        selectCurrencyPurchase: 'انتخاب خرید ارز',
        amount: 'مبلغ',
        shipmentDate: 'تاریخ حمل',
        receivedDate: 'تاریخ دریافت',
        referenceNumber: 'شماره مرجع',
        notes: 'یادداشت',
        correctionReason: 'دلیل اصلاح',
        correctionReasonPlaceholder: 'دلیل اصلاح سند حمل را وارد کنید',
        correctionReasonError: 'وارد کردن دلیل اصلاح الزامی است.',
        submitCorrection: 'ارسال درخواست اصلاح',
        submittingCorrection: 'در حال ارسال درخواست اصلاح...',
        submitCreate: 'ارسال درخواست ایجاد',
        submittingCreate: 'در حال ارسال درخواست...',
        selectPurchaseError: 'لطفاً یک خرید ارز انتخاب کنید.',
        invalidAmountError: 'مبلغ سند حمل باید بیشتر از صفر باشد.',
        saveError: 'ارسال درخواست سند حمل انجام نشد.',
      },

      invoices: {
        title:
          'فاکتورها',

        description:
          'مدیریت فاکتورهای اسناد حمل و مقادیر مالی آن‌ها',

        addInvoice:
          'افزودن فاکتور',

        company:
          'شرکت',

        order:
          'ثبت سفارش',

        documentPart:
          'ردیف سند',

        partValue:
          'پارت {{count}}',

        purchaseAmount:
          'مبلغ خرید ارز',

        fob:
          'مبلغ FOB',

        freight:
          'کرایه حمل',

        total:
          'مبلغ کل',

        remainingAmount:
          'مبلغ باقی‌مانده',

        currency:
          'ارز',

        submissionDate:
          'تاریخ ارائه',

        actions:
          'عملیات',

        empty:
          'فاکتوری ثبت نشده است.',

        loading:
          'در حال بارگذاری فاکتورها...',

        loadError:
          'بارگذاری اطلاعات فاکتورها انجام نشد.',
      },

      invoiceForm: {
        addTitle:
          'افزودن فاکتور',

        editTitle:
          'ویرایش فاکتور',

        addDescription:
          'ثبت فاکتور برای یک سند حمل',

        editDescription:
          'اطلاعات مالی فاکتور را ویرایش کنید.',

        shipmentPart:
          'سند حمل',

        selectShipmentPart:
          'انتخاب سند حمل',

        noReference:
          'بدون شماره مرجع',

        fobAmount:
          'مبلغ FOB',

        freightAmount:
          'کرایه حمل',

        submissionDate:
          'تاریخ ارائه',

        createInvoice:
          'ایجاد فاکتور',

        saveChanges:
          'ذخیره تغییرات',

        saving:
          'در حال ذخیره...',

        close:
          'بستن فرم فاکتور',

        selectShipmentError:
          'لطفاً یک سند حمل انتخاب کنید.',

        invalidFobError:
          'مبلغ FOB نمی‌تواند منفی باشد.',

        invalidFreightError:
          'کرایه حمل نمی‌تواند منفی باشد.',

        submissionDateError:
          'لطفاً تاریخ ارائه را انتخاب کنید.',

        saveError:
          'ذخیره فاکتور انجام نشد.',
      },

      paymentInstruments: {
        title:
          'ابزارهای پرداخت',

        description:
          'مدیریت شماره ابزارهای پرداخت مرتبط با ثبت سفارش‌ها',

        addPaymentInstrument:
          'افزودن ابزار پرداخت',

        company:
          'شرکت',

        order:
          'ثبت سفارش',

        instrumentNumber:
          'شماره ابزار پرداخت',

        actions:
          'عملیات',

        empty:
          'ابزار پرداختی ثبت نشده است.',

        loading:
          'در حال بارگذاری ابزارهای پرداخت...',

        loadError:
          'بارگذاری اطلاعات ابزارهای پرداخت انجام نشد.',
      },

      paymentInstrumentForm: {
        addTitle:
          'افزودن ابزار پرداخت',

        editTitle:
          'ویرایش ابزار پرداخت',

        addDescription:
          'اتصال یک ابزار پرداخت به ثبت سفارش',

        editDescription:
          'شماره ابزار پرداخت را ویرایش کنید.',

        registrationOrder:
          'ثبت سفارش',

        selectRegistrationOrder:
          'انتخاب ثبت سفارش',

        instrumentNumber:
          'شماره ابزار پرداخت',

        instrumentNumberPlaceholder:
          'مثال: PI-2026-0001',

        create:
          'ایجاد',

        saveChanges:
          'ذخیره تغییرات',

        saving:
          'در حال ذخیره...',

        close:
          'بستن فرم ابزار پرداخت',

        selectOrderError:
          'لطفاً یک ثبت سفارش انتخاب کنید.',

        instrumentNumberError:
          'لطفاً شماره ابزار پرداخت را وارد کنید.',

        saveError:
          'ذخیره ابزار پرداخت انجام نشد.',
      },

      notifications: {
        title:
          'اعلان‌ها',

        description:
          'بررسی هشدارهای سررسید ایجادشده برای خریدهای ارز',

        company:
          'شرکت',

        order:
          'ثبت سفارش',

        purchase:
          'خرید ارز',

        purchaseDate:
          'تاریخ خرید',

        deadline:
          'سررسید',

        alert:
          'نوع هشدار',

        generatedAt:
          'زمان ایجاد',

        empty:
          'اعلانی ثبت نشده است.',

        loading:
          'در حال بارگذاری اعلان‌ها...',

        loadError:
          'بارگذاری اعلان‌ها انجام نشد.',

        types: {
          NINETY_DAYS:
            '۹۰ روز مانده',

          SIXTY_DAYS:
            '۶۰ روز مانده',

          THIRTY_DAYS:
            '۳۰ روز مانده',

          TWENTY_DAYS:
            '۲۰ روز مانده',

          TEN_DAYS:
            '۱۰ روز مانده',

          FIVE_DAYS:
            '۵ روز مانده',

          LAST_DAY:
            'آخرین روز',

          OVERDUE:
            'سررسید گذشته',
        },
      },

      login: {
        title:
          'TradeFlowAI',

        subtitle:
          'سامانه مدیریت تأمین مالی تجارت',

        username:
          'نام کاربری',

        password:
          'رمز عبور',

        signIn:
          'ورود',

        signingIn:
          'در حال ورود...',

        loginFailed:
          'ورود ناموفق بود.',
      },

      forbidden: {
        title:
          'دسترسی غیرمجاز',

        message:
          'شما مجوز دسترسی به این صفحه را ندارید.',

        backToDashboard:
          'بازگشت به داشبورد',

        contactAdministrator:
          'اگر به دسترسی بیشتری نیاز دارید، با مدیر سامانه تماس بگیرید.',
      },

      auth: {
        checkingSession:
          'در حال بررسی نشست کاربری...',
      },

      statCard: {
        attention:
          'نیازمند توجه',

        critical:
          'بحرانی',
      },

      logoutFailed:
        'خروج از سامانه انجام نشد.',

      approvals: {
        title:
          'درخواست‌های تأیید',

        subtitle:
          'درخواست‌های در انتظار بررسی و تأیید را بررسی کنید.',

        loading:
          'در حال بارگذاری درخواست‌های تأیید...',

        empty:
          'درخواست تأییدی در انتظار بررسی وجود ندارد.',

        loadError:
          'بارگذاری درخواست‌های تأیید انجام نشد.',

        maker:
          'ثبت‌کننده درخواست',

        createdAt:
          'زمان ثبت',

        reason:
          'دلیل درخواست',

        approve:
          'تأیید درخواست',

        approveVoid:
          'تأیید ابطال',

        reject:
          'رد درخواست',

        confirmApprove:
          'آیا از تأیید این درخواست مطمئن هستید؟',

        confirmVoidApprove:
          'آیا از تأیید ابطال این خرید ارز مطمئن هستید؟',

        rejectReasonPrompt:
          'دلیل رد درخواست را وارد کنید:',

        rejectReasonRequired:
          'وارد کردن دلیل رد الزامی است.',

        approveError:
          'تأیید درخواست انجام نشد.',

        rejectError:
          'رد درخواست انجام نشد.',

        voidNoticeTitle:
          'این درخواست برای ابطال خرید ارز است',

        voidNoticeDescription:
          'در صورت تأیید، این خرید ارز باطل خواهد شد و دیگر در محاسبات فعال مالی در نظر گرفته نمی‌شود.',
        shipmentVoidNoticeTitle: 'این درخواست برای ابطال سند حمل است',
        shipmentVoidNoticeDescription: 'در صورت تأیید، این سند حمل باطل شده و از محاسبات مبلغ مستندشده خارج می‌شود.',

        operations: {
          create:
            'درخواست ایجاد',

          correct:
            'درخواست اصلاح',

          void:
            'درخواست ابطال',
        },

        targets: {
          currencyPurchase:
            'خرید ارز',

          shipmentPart:
            'سند حمل',
        },

        status: {
          pending:
            'در انتظار تأیید',
        },

        fields: {
          field:
            'فیلد',

          current:
            'مقدار فعلی',

          proposed:
            'مقدار پیشنهادی',

          amount:
            'مبلغ خرید',

          currency:
            'ارز',

          purchaseDate:
            'تاریخ خرید',

          registrationOrder:
            'شناسه ثبت سفارش',

          voided: 'باطل‌شده',
          currencyPurchase: 'شناسه خرید ارز',
          shipmentDate: 'تاریخ حمل',
          receivedDate: 'تاریخ دریافت',
          referenceNumber: 'شماره مرجع',
          notes: 'یادداشت',
        },
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
        approvals: 'Approval Requests',
        auditTrail: 'Audit Trail',
      },

      auditTrail: {
        title: 'Audit Trail',
        description: 'Immutable history of sensitive operations, data changes, and Maker-Checker decisions.',
        loading: 'Loading audit events...',
        loadError: 'Failed to load the audit trail.',
        empty: 'No audit events have been recorded yet.',
        time: 'Time',
        actor: 'Actor',
        action: 'Action',
        target: 'Target',
        targetId: 'Target ID',
        reason: 'Reason',
        details: 'Details',
        showDetails: 'Show',
        hideDetails: 'Hide',
        before: 'Before',
        after: 'After',
        metadata: 'Request Metadata',
        system: 'System',
        actions: {
          CREATE: 'Create',
          UPDATE: 'Update',
          VOID: 'Void',
          DELETE: 'Delete',
          REQUEST_SUBMITTED: 'Request Submitted',
          REQUEST_APPROVED: 'Request Approved',
          REQUEST_REJECTED: 'Request Rejected',
        },
        targets: {
          'companies.company': 'Company',
          'trade_orders.registrationorder': 'Registration Order',
          'trade_orders.paymentinstrument': 'Payment Instrument',
          'trade_orders.currencypurchase': 'Currency Purchase',
          'trade_orders.shipmentpart': 'Shipment Part',
          'documents.invoice': 'Invoice',
          currency_purchase: 'Currency Purchase',
          shipment_part: 'Shipment Part',
        },
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

      registrationOrderForm: {
        addTitle: 'Add Registration Order',
        editTitle: 'Edit Registration Order',

        addDescription:
          'Create a new registered trade order.',
        editDescription:
          'Update registration order information.',

        company: 'Company',
        selectCompany: 'Select a company',
        loadingCompanies: 'Loading companies...',

        orderNumber: 'Order Number',
        orderNumberPlaceholder: 'e.g. TF-USD-002',

        registeredAmount: 'Registered Amount',
        registeredAmountPlaceholder: 'e.g. 50000',

        currency: 'Currency',
        currencyPlaceholder: 'USD',

        activeOrder: 'Active registration order',

        saveChanges: 'Save Changes',
        createOrder: 'Create Order',
        saving: 'Saving...',
        creating: 'Creating...',

        selectCompanyError:
          'Please select a company.',

        requiredFieldsError:
          'Please complete all required fields.',

        invalidAmountError:
          'Registered amount must be greater than zero.',

        invalidCurrencyError:
          'Currency must be a valid 3-letter code.',
      },

      currencyPurchases: {
        title: 'Currency Purchases',
        description:
          'Manage currency purchases and their deadlines.',

        addPurchase:
          'Add Currency Purchase',

        company:
          'Company',

        orderNumber:
          'Order Number',

        amount:
          'Amount',

        currency:
          'Currency',

        purchaseDate:
          'Purchase Date',

        deadline:
          'Deadline',

        actions:
          'Actions',

        empty:
          'No currency purchases found.',

        loading:
          'Loading currency purchases...',

        loadError:
          'Failed to load currency purchases.',

        requestVoid:
          'Request Void',

        voidTitle:
          'Request Currency Purchase Void',

        voidDescription:
          'Enter the reason for submitting this void request.',

        voidReason:
          'Void Reason',

        voidReasonRequired:
          'A void reason is required.',

        voidError:
          'Failed to submit void request.',

        voidSubmitting:
          'Submitting request...',

        submitVoid:
          'Submit Void Request',

        voided: 'Voided',
      },

      currencyPurchaseForm: {
        addTitle:
          'Add Currency Purchase',

        editTitle:
          'Request Currency Purchase Correction',

        addDescription:
          'Submit a new currency purchase request.',

        editDescription:
          'Correct the amount or purchase date and submit it for approval.',

        registrationOrder:
          'Registration Order',

        selectOrder:
          'Select a registration order',

        loadingOrders:
          'Loading orders...',

        currency:
          'Currency',

        purchaseAmount:
          'Purchase Amount',

        purchaseAmountPlaceholder:
          'e.g. 50000',

        purchaseDate:
          'Purchase Date',

        correctionReason:
          'Correction Reason',

        correctionReasonPlaceholder:
          'Enter the reason for this correction',

        correctionReasonError:
          'A correction reason is required.',

        saveChanges:
          'Submit Correction Request',

        createPurchase:
          'Submit Purchase Request',

        saving:
          'Submitting correction...',

        creating:
          'Submitting request...',

        selectOrderError:
          'Please select a registration order.',

        invalidAmountError:
          'Purchase amount must be greater than zero.',

        purchaseDateError:
          'Please select a purchase date.',

        currencyUnavailableError:
          'Currency is unavailable for the selected order.',
      },

      shipmentParts: {
        title: 'Shipment Parts',
        description:
          'Track shipment allocations linked to currency purchases.',

        addShipmentPart:
          'Add Shipment Part',

        company:
          'Company',

        orderNumber:
          'Order Number',

        reference:
          'Reference',

        amount:
          'Amount',

        currency:
          'Currency',

        shipmentDate:
          'Shipment Date',

        receivedDate:
          'Received Date',

        notes:
          'Notes',

        actions:
          'Actions',

        empty:
          'No shipment parts found.',

        loading:
          'Loading shipment parts...',

        loadError:
          'Failed to load shipment data.',

        requestVoid:
          'Request Void',

        voided:
          'Voided',

        voidTitle:
          'Request Shipment Void',

        voidDescription:
          'Enter the reason for submitting this shipment void request.',

        voidReason:
          'Void Reason',

        voidReasonRequired:
          'A void reason is required.',

        voidError:
          'Failed to submit shipment void request.',

        voidSubmitting:
          'Submitting request...',

        submitVoid:
          'Submit Void Request',
        voidReasonPrompt: 'Enter the reason for voiding this shipping document:',

      },

      shipmentPartForm: {
        addTitle: 'Add Shipping Document',
        editTitle: 'Request Shipping Document Correction',
        addDescription: 'Submit a new shipping document request for a currency purchase.',
        editDescription: 'Correct shipping document information and submit it for approval.',
        currencyPurchase: 'Currency Purchase',
        selectCurrencyPurchase: 'Select currency purchase',
        amount: 'Amount',
        shipmentDate: 'Shipment Date',
        receivedDate: 'Received Date',
        referenceNumber: 'Reference Number',
        notes: 'Notes',
        correctionReason: 'Correction Reason',
        correctionReasonPlaceholder: 'Enter the reason for this correction',
        correctionReasonError: 'A correction reason is required.',
        submitCorrection: 'Submit Correction Request',
        submittingCorrection: 'Submitting correction...',
        submitCreate: 'Submit Create Request',
        submittingCreate: 'Submitting request...',
        selectPurchaseError: 'Please select a currency purchase.',
        invalidAmountError: 'Shipment amount must be greater than zero.',
        saveError: 'Failed to submit shipping document request.',
      },

      invoices: {
        title:
          'Invoices',

        description:
          'Manage shipment invoices and financial document values.',

        addInvoice:
          'Add Invoice',

        company:
          'Company',

        order:
          'Order',

        documentPart:
          'Document Row',

        partValue:
          'Part {{count}}',

        purchaseAmount:
          'Currency Purchase Amount',

        fob:
          'FOB',

        freight:
          'Freight',

        total:
          'Total',

        remainingAmount:
          'Remaining Amount',

        currency:
          'Currency',

        submissionDate:
          'Submission Date',

        actions:
          'Actions',

        empty:
          'No invoices found.',

        loading:
          'Loading invoices...',

        loadError:
          'Failed to load invoice data.',
      },

      invoiceForm: {
        addTitle:
          'Add Invoice',

        editTitle:
          'Edit Invoice',

        addDescription:
          'Create an invoice for a shipment part.',

        editDescription:
          'Update invoice financial details.',

        shipmentPart:
          'Shipment Part',

        selectShipmentPart:
          'Select shipment part',

        noReference:
          'No reference',

        fobAmount:
          'FOB Amount',

        freightAmount:
          'Freight Amount',

        submissionDate:
          'Submission Date',

        createInvoice:
          'Create Invoice',

        saveChanges:
          'Save Changes',

        saving:
          'Saving...',

        close:
          'Close invoice form',

        selectShipmentError:
          'Please select a shipment part.',

        invalidFobError:
          'FOB amount cannot be negative.',

        invalidFreightError:
          'Freight amount cannot be negative.',

        submissionDateError:
          'Please select a submission date.',

        saveError:
          'Failed to save invoice.',
      },

      paymentInstruments: {
        title:
          'Payment Instruments',

        description:
          'Manage payment instrument numbers linked to registration orders.',

        addPaymentInstrument:
          'Add Payment Instrument',

        company:
          'Company',

        order:
          'Order',

        instrumentNumber:
          'Instrument Number',

        actions:
          'Actions',

        empty:
          'No payment instruments found.',

        loading:
          'Loading payment instruments...',

        loadError:
          'Failed to load payment instruments.',
      },

      paymentInstrumentForm: {
        addTitle:
          'Add Payment Instrument',

        editTitle:
          'Edit Payment Instrument',

        addDescription:
          'Link a payment instrument to a registration order.',

        editDescription:
          'Update the payment instrument number.',

        registrationOrder:
          'Registration Order',

        selectRegistrationOrder:
          'Select registration order',

        instrumentNumber:
          'Instrument Number',

        instrumentNumberPlaceholder:
          'Example: PI-2026-0001',

        create:
          'Create',

        saveChanges:
          'Save Changes',

        saving:
          'Saving...',

        close:
          'Close payment instrument form',

        selectOrderError:
          'Please select a registration order.',

        instrumentNumberError:
          'Please enter an instrument number.',

        saveError:
          'Failed to save payment instrument.',
      },

      notifications: {
        title:
          'Notifications',

        description:
          'Review deadline alerts generated for currency purchases.',

        company:
          'Company',

        order:
          'Order',

        purchase:
          'Purchase',

        purchaseDate:
          'Purchase Date',

        deadline:
          'Deadline',

        alert:
          'Alert',

        generatedAt:
          'Generated At',

        empty:
          'No notifications found.',

        loading:
          'Loading notifications...',

        loadError:
          'Failed to load notifications.',

        types: {
          NINETY_DAYS:
            '90 Days Remaining',

          SIXTY_DAYS:
            '60 Days Remaining',

          THIRTY_DAYS:
            '30 Days Remaining',

          TWENTY_DAYS:
            '20 Days Remaining',

          TEN_DAYS:
            '10 Days Remaining',

          FIVE_DAYS:
            '5 Days Remaining',

          LAST_DAY:
            'Last Day',

          OVERDUE:
            'Overdue',
        },
      },

      login: {
        title:
          'TradeFlowAI',

        subtitle:
          'Trade Finance Management System',

        username:
          'Username',

        password:
          'Password',

        signIn:
          'Sign in',

        signingIn:
          'Signing in...',

        loginFailed:
          'Login failed.',
      },

      forbidden: {
        title:
          'Access Denied',

        message:
          'You do not have permission to access this page.',

        backToDashboard:
          'Back to Dashboard',

        contactAdministrator:
          'Please contact your administrator if you need additional access.',
      },

      auth: {
        checkingSession:
          'Checking your session...',
      },

      statCard: {
        attention:
          'Attention',

        critical:
          'Critical',
      },

      logoutFailed:
        'Logout failed.',

      approvals: {
        title: 'Approval Requests',
        subtitle: 'Review pending Maker-Checker requests.',
        loading: 'Loading approval requests...',
        empty: 'There are no pending approval requests.',
        loadError: 'Failed to load approval requests.',
        maker: 'Maker',
        createdAt: 'Created At',
        reason: 'Reason',
        approve: 'Approve',
        approveVoid: 'Approve Void',
        reject: 'Reject',
        confirmApprove: 'Approve this request?',
        confirmVoidApprove: 'Approve this void request?',
        rejectReasonPrompt: 'Enter rejection reason:',
        rejectReasonRequired: 'A rejection reason is required.',
        approveError: 'Failed to approve request.',
        rejectError: 'Failed to reject request.',
        voidNoticeTitle: 'This request will void a currency purchase',
        voidNoticeDescription: 'If approved, the purchase will be excluded from active financial calculations.',
        shipmentVoidNoticeTitle: 'This request will void a shipping document',
        shipmentVoidNoticeDescription: 'If approved, the shipping document will be excluded from documented-amount calculations.',
        operations: {
          create: 'Create Request',
          correct: 'Correction Request',
          void: 'Void Request',
        },
        targets: {
          currencyPurchase: 'Currency Purchase',
          shipmentPart: 'Shipping Document',
        },
        status: {
          pending: 'Pending Approval',
        },
        fields: {
          field: 'Field',
          current: 'Current Value',
          proposed: 'Proposed Value',
          amount: 'Amount',
          currency: 'Currency',
          purchaseDate: 'Purchase Date',
          registrationOrder: 'Registration Order ID',
          currencyPurchase: 'Currency Purchase ID',
          shipmentDate: 'Shipment Date',
          receivedDate: 'Received Date',
          referenceNumber: 'Reference Number',
          notes: 'Notes',
          voided: 'Voided',
        },
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