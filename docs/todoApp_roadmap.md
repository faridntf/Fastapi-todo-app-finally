# TodoApp --- نقشه راه پیاده‌سازی با FastAPI

> این سند «جواب پروژه» نیست؛ نقشه‌ی راه اجرای آن است. در هر مرحله ابتدا
> مفهوم را یاد بگیر، سپس خودت پیاده‌سازی کن و بعد نتیجه را بررسی کن. عمداً
> کد آماده در این سند قرار نگرفته است.

## 1. هدف پروژه

ساخت یک REST API برای مدیریت کارهای شخصی (Todo) با قابلیت‌های زیر:

-   ثبت‌نام و مدیریت حساب کاربری
-   ورود و خروج امن
-   Authentication با JWT
-   Authorization بر اساس Role و مالکیت منابع
-   مدیریت Profile
-   CRUD برای Task
-   دسته‌بندی Taskها و دسته‌بندی تو‌در‌تو
-   PostgreSQL به‌عنوان پایگاه داده
-   SQLAlchemy برای ORM
-   Alembic برای Migration
-   Pydantic برای Validation و قرارداد ورودی/خروجی API

### فناوری‌ها

-   Python
-   FastAPI
-   PostgreSQL
-   SQLAlchemy
-   Alembic
-   Pydantic
-   JWT
-   Password Hashing
-   Pytest در مرحله تست

------------------------------------------------------------------------

# 2. قوانین آموزشی پروژه

در طول پروژه این ترتیب را حفظ کن:

1.  مسئله را بفهم.
2.  مدل داده و قرارداد API را مشخص کن.
3.  خودت پیاده‌سازی کن.
4.  برنامه را اجرا و خطاها را بررسی کن.
5.  بعد از درست کار کردن، Refactor کن.
6.  در پایان هر بخش تست بنویس.

از قرار دادن Secret، رمز دیتابیس یا کلید JWT در سورس پروژه و Git خودداری
کن.

------------------------------------------------------------------------

# 3. مدل داده مبنا

Schema فعلی پروژه شامل موارد زیر است:

## User

اطلاعات اصلی حساب:

-   id
-   username
-   email
-   password
-   phone_number
-   created_at
-   updated_at
-   role
-   is_active
-   is_verified
-   last_login
-   is_delete
-   deleted_at

### قواعد

-   `id` کلید اصلی است.
-   `username` یکتا و Index شده باشد.
-   `email` یکتا و Index شده باشد.
-   `phone_number` در طراحی فعلی یکتا است.
-   مقدار `password` در دیتابیس باید **Hash شده** ذخیره شود؛ نام ستون
    طبق تصمیم پروژه همان `password` باقی می‌ماند.
-   `role` از Enum مربوط به UserRole استفاده کند.
-   `is_delete` مشخص کند حساب در وضعیت حذف‌شده قرار دارد یا خیر.
-   `deleted_at` زمان حذف را ثبت کند.
-   منطق `is_delete` و `deleted_at` باید همیشه با هم سازگار بماند.

### UserRole

-   Admin
-   User
-   Guest
-   Super_User

------------------------------------------------------------------------

## Profile

اطلاعات تکمیلی کاربر:

-   id
-   bio
-   profile_url
-   national_id
-   first_name
-   last_name
-   date_of_birth
-   gender
-   website
-   address
-   user_id_fk

رابطه:

**User 1 ↔ 1 Profile**

`user_id_fk` باید یکتا باشد تا دیتابیس نیز One-to-One بودن رابطه را
تضمین کند.

### Gender

-   male
-   Female
-   Other
-   Prefer_not_to_say

قبل از Migration اولیه، درباره یکدست بودن شیوه نام‌گذاری مقادیر Enum
تصمیم بگیر و همان convention را در کل پروژه حفظ کن.

------------------------------------------------------------------------

## Task

-   id
-   title
-   description
-   is_completed
-   created_at
-   updated_at
-   category_id_fk
-   user_id_fk

روابط:

**User 1 → N Task**

**Category 1 → N Task**

Task باید متعلق به User باشد.

درباره `category_id_fk` تصمیم صریح بگیر: آیا Category برای Task اجباری
است یا اختیاری؟ اگر Task بدون Category مجاز است، nullable بودن FK باید
همین تصمیم را منعکس کند.

------------------------------------------------------------------------

## Category

-   id
-   category_name
-   parent_id_fk
-   description

`parent_id_fk` به خود جدول Category اشاره می‌کند.

رابطه:

**Category 1 → N Child Categories**

نمونه مفهومی:

Work → Programming → Backend

قبل از پیاده‌سازی مشخص کن Categoryها سراسری هستند یا متعلق به یک User.
اگر Category شخصی است، Schema باید مالکیت آن توسط User را نیز نمایش دهد.
این تصمیم مستقیماً روی Authorization اثر دارد.

------------------------------------------------------------------------

## Token / Session

Schema اولیه:

-   id
-   token
-   expiration
-   user_id_fk

این جدول در مرحله Authentication عمداً دوباره بررسی خواهد شد. پیش از
نهایی کردن آن باید تفاوت Access Token، Refresh Token، Revocation و
Logout را بفهمی.

**معیار پایان مرحله طراحی:** بتوانی تمام Relationshipها، Nullableها،
Unique Constraintها و رفتار حذف رکوردها را بدون مراجعه به کد توضیح بدهی.

------------------------------------------------------------------------

# 4. مرحله صفر --- تعریف رفتار سیستم

قبل از ساخت فایل‌ها، Use Caseهای اصلی را بنویس.

حداقل رفتارهای مورد انتظار:

-   کاربر ثبت‌نام می‌کند.
-   کاربر Login می‌کند.
-   کاربر Profile خود را می‌بیند/ویرایش می‌کند.
-   کاربر Task ایجاد می‌کند.
-   کاربر فقط Taskهای مجاز خودش را مدیریت می‌کند.
-   کاربر Category ایجاد و استفاده می‌کند.
-   سیستم Role کاربر را برای عملیات مدیریتی بررسی می‌کند.
-   کاربر Logout می‌کند.
-   حساب می‌تواند غیرفعال یا Soft Delete شود.

### سؤال‌های طراحی

-   آیا User غیرفعال اجازه Login دارد؟
-   User حذف‌شده چه رفتاری دارد؟
-   آیا Admin می‌تواند Task کاربران را مشاهده کند؟
-   آیا Super_User با Admin فرق دارد؟
-   Guest دقیقاً چه مجوزی دارد؟
-   Category شخصی است یا عمومی؟
-   حذف Category با Taskهای آن چه می‌کند؟
-   حذف User با Profile، Task و Token/Sessionهای او چه می‌کند؟

**معیار پایان:** برای تمام سؤال‌های بالا یک تصمیم مکتوب داشته باش.

------------------------------------------------------------------------

# 5. ایجاد پروژه و محیط توسعه

کارهایی که باید انجام دهی:

-   Repository پروژه را ایجاد کن.
-   Virtual Environment بساز.
-   Dependencyهای اصلی را نصب کن.
-   فایل `.gitignore` ایجاد کن.
-   ساختار اولیه برنامه را بساز.
-   FastAPI application را بالا بیاور.
-   یک endpoint بسیار ساده فقط برای اطمینان از اجرای برنامه داشته باش.

ساختار پروژه باید مسئولیت‌ها را از هم جدا کند. در این مرحله درباره بخش‌های
زیر فکر کن:

-   entry point برنامه
-   configuration
-   database
-   models
-   schemas
-   routers
-   authentication/security
-   services یا لایه business logic
-   tests

ساختار را بیش از حد معماری‌زده نکن. هدف یادگیری است، نه ساخت وزارتخانه
برای چهار endpoint.

**معیار پایان:** برنامه بدون خطا اجرا شود و ساختار هر پوشه برایت قابل
توضیح باشد.

------------------------------------------------------------------------

# 6. Configuration و Environment Variables

اطلاعات محیطی را از منطق برنامه جدا کن.

مواردی که باید قابل تنظیم باشند:

-   Database URL
-   JWT secret/key
-   JWT algorithm
-   Access Token expiration
-   در صورت استفاده، Refresh Token expiration
-   سایر تنظیمات وابسته به محیط

### یادگیری

-   Environment Variable چیست؟
-   چرا Secret نباید داخل Git باشد؟
-   Pydantic Settings چه مسئله‌ای را حل می‌کند؟
-   تفاوت config توسعه و production چیست؟

**معیار پایان:** بتوانی تنظیمات محیطی را بدون تغییر کد برنامه عوض کنی.

------------------------------------------------------------------------

# 7. PostgreSQL

یک Database مخصوص پروژه ایجاد کن.

موارد بررسی:

-   اتصال دستی به PostgreSQL
-   ساخت Database
-   User/Role دیتابیس در صورت نیاز
-   Connection String
-   دسترسی‌های لازم
-   تست اتصال از برنامه

در این مرحله هنوز جدول‌ها را دستی نساز.

**معیار پایان:** برنامه بتواند اتصال صحیح به PostgreSQL برقرار کند.

------------------------------------------------------------------------

# 8. SQLAlchemy Setup

SQLAlchemy را به برنامه متصل کن.

مفاهیمی که باید بفهمی:

-   Engine
-   Session
-   transaction
-   commit
-   rollback
-   flush
-   refresh
-   ORM
-   Declarative Model
-   Connection Pool
-   Dependency برای Database Session

اگر دوره‌ات SQLAlchemy 2.x را آموزش می‌دهد، convention همان نسخه را در کل
پروژه یکدست نگه دار.

**معیار پایان:** بتوانی چرخه عمر یک Database Session در یک Request را
توضیح بدهی.

------------------------------------------------------------------------

# 9. ساخت Modelها

Modelها را بر اساس ERD بساز.

ترتیب پیشنهادی:

1.  User و Enumهای مربوط
2.  Profile
3.  Category و self relationship
4.  Task
5.  Token/Session پس از تصمیم مرحله Authentication

برای هر Model بررسی کن:

-   Primary Key
-   Foreign Key
-   Unique
-   Index
-   Nullable
-   Default
-   Relationship
-   cascade
-   رفتار حذف

### تمرین مهم

قبل از اجرای Migration، برای هر رابطه روی کاغذ مشخص کن:

-   cardinality چیست؟
-   FK در کدام جدول است؟
-   ORM relationship در کدام سمت/سمت‌ها لازم است؟
-   هنگام حذف Parent چه اتفاقی باید بیفتد؟

**معیار پایان:** Modelها ERD را بدون تناقض نمایش دهند.

------------------------------------------------------------------------

# 10. Alembic

Alembic را راه‌اندازی کن.

### باید یاد بگیری

-   Migration چیست؟
-   چرا `create_all` جای Migration را نمی‌گیرد؟
-   Revision چیست؟
-   Upgrade چیست؟
-   Downgrade چیست؟
-   Autogenerate چه کاری انجام می‌دهد؟
-   چرا Migration تولیدشده باید قبل از اجرا بازبینی شود؟

### تمرین

Migration اولیه را از Modelها ایجاد کن، فایل Migration را بخوان، سپس آن
را روی PostgreSQL اجرا کن.

بعد یک تغییر کوچک کنترل‌شده در Schema ایجاد کن و Migration دوم بساز تا
واقعاً چرخه Migration را تجربه کنی.

**معیار پایان:** بتوانی دیتابیس خالی را فقط با Migrationها به آخرین
Schema برسانی.

------------------------------------------------------------------------

# 11. Pydantic Schemaها

ORM Model را مستقیماً قرارداد API فرض نکن.

برای هر Resource مشخص کن چه Schemaهایی لازم است. معمولاً نیازها حول این
عملیات‌اند:

-   Create
-   Update
-   Response
-   Internal data

### User

مراقب باش Response هیچ‌گاه Password Hash را برنگرداند.

### Profile

بین فیلدهای قابل تغییر توسط User و اطلاعات داخلی سیستم تفاوت قائل شو.

### Task

Validationهای `title`، `description` و داده‌های ورودی را مشخص کن.

### Category

Validation نام و parent را مشخص کن.

### یادگیری

-   Validation
-   serialization
-   optional field
-   default
-   response model
-   تفاوت ORM Model و Pydantic Model

**معیار پایان:** هیچ endpointی داده حساس یا ستون‌های داخلی ناخواسته را
expose نکند.

------------------------------------------------------------------------

# 12. ثبت‌نام User

اولین جریان واقعی حساب کاربری را پیاده‌سازی کن.

ترتیب منطقی:

Client → Validation → بررسی تکراری نبودن اطلاعات → Hash Password → ذخیره
User → Response امن

### مواردی که باید مدیریت شوند

-   Username تکراری
-   Email تکراری
-   Phone Number تکراری، مطابق تصمیم Schema
-   Password نامعتبر
-   داده ناقص
-   خطای Database

### امنیت

Password خام:

-   نباید در Database ذخیره شود.
-   نباید در Response برگردد.
-   نباید در Log ثبت شود.

**معیار پایان:** User جدید با Password Hash شده ساخته شود و هیچ
Passwordای در Response دیده نشود.

------------------------------------------------------------------------

# 13. Password Hashing

قبل از Login، Hashing را مستقل یاد بگیر.

مفاهیم:

-   Hash با Encryption یکی نیست.
-   Password Hash باید Salt و الگوریتم مناسب داشته باشد.
-   مقایسه Password با Hash باید توسط ابزار مناسب انجام شود.
-   خودت الگوریتم رمزنگاری اختراع نکن. تاریخ نشان داده انسان‌ها در این
    قسمت اعتمادبه‌نفس بیشتری از استعدادشان دارند.

دو عملیات مفهومی لازم داری:

-   Hash کردن Password هنگام ثبت‌نام/تغییر رمز
-   Verify کردن Password هنگام Login

**معیار پایان:** بتوانی توضیح بدهی چرا Password اصلی از Hash قابل
بازیابی نیست و Login چگونه بدون بازیابی آن انجام می‌شود.

------------------------------------------------------------------------

# 14. Login

جریان Login:

Credentials → پیدا کردن User → بررسی وضعیت حساب → Verify Password → صدور
Token

### شرایط شکست

-   User وجود ندارد.
-   Password اشتباه است.
-   حساب غیرفعال است.
-   حساب Soft Delete شده است.
-   وضعیت حساب اجازه Login نمی‌دهد.

در پاسخ خطا مراقب Information Leakage باش.

در Login موفق، `last_login` را مطابق سیاست پروژه به‌روزرسانی کن.

**معیار پایان:** فقط User معتبر و مجاز بتواند Token دریافت کند.

------------------------------------------------------------------------

# 15. JWT Authentication

این بخش را با حوصله انجام بده. JWT صرفاً سه تکه متن با نقطه بینشان نیست.

### مفاهیم

-   Header
-   Payload
-   Signature
-   Claims
-   `sub`
-   `exp`
-   issued time در صورت نیاز
-   Token expiration
-   Secret/Private Key
-   Algorithm

### ابتدا تصمیم بگیر

-   `sub` چه چیزی را نمایش می‌دهد؟
-   Access Token چند دقیقه معتبر است؟
-   چه اطلاعاتی واقعاً باید داخل Token باشد؟
-   آیا Role داخل Token قرار می‌گیرد یا هر بار از DB خوانده می‌شود؟
-   با تغییر Role کاربر، Token قبلی چه رفتاری دارد؟

### هشدار

اطلاعات حساس را داخل JWT Payload قرار نده. JWT امضاشده الزاماً
رمزگذاری‌شده نیست.

**معیار پایان:** بتوانی Token معتبر، منقضی‌شده و دستکاری‌شده را از هم
تفکیک و رفتار سیستم را توضیح بدهی.

------------------------------------------------------------------------

# 16. Current User Dependency

یک سازوکار مرکزی برای استخراج User فعلی طراحی کن.

جریان مفهومی:

Authorization Header → Bearer Token → Decode/Verify → استخراج identity →
دریافت User → بررسی وضعیت → Current User

این منطق نباید در تک‌تک endpointها کپی شود.

**معیار پایان:** endpoint محافظت‌شده بدون Token یا با Token نامعتبر قابل
استفاده نباشد.

------------------------------------------------------------------------

# 17. Authorization

Authentication پاسخ می‌دهد:

> این شخص کیست؟

Authorization پاسخ می‌دهد:

> این شخص اجازه انجام این کار را دارد؟

دو نوع Authorization برای این پروژه مهم است.

### Role-based

مثلاً عملیات مدیریتی فقط برای Roleهای مشخص.

### Ownership-based

User عادی نباید با تغییر ID در URL بتواند Task کاربر دیگری را بخواند یا
تغییر دهد.

این مورد را برای Profile، Task و Categoryهای شخصی بررسی کن.

**معیار پایان:** تغییر دستی ID منابع باعث دسترسی به داده User دیگر نشود.

------------------------------------------------------------------------

# 18. Profile

Endpointهای مورد نیاز Profile را طراحی و سپس پیاده‌سازی کن.

حداقل عملیات:

-   مشاهده Profile خود
-   ایجاد/تکمیل Profile طبق سیاست پروژه
-   Update Profile

تصمیم بگیر Profile هنگام Register خودکار ساخته می‌شود یا بعداً توسط User.

### تست‌ها

-   User A نمی‌تواند Profile خصوصی User B را تغییر دهد.
-   `user_id_fk` از سمت Client قابل جعل نباشد.
-   One-to-One بودن Profile حفظ شود.

**معیار پایان:** هر User حداکثر یک Profile داشته باشد.

------------------------------------------------------------------------

# 19. Category

CRUD مناسب Category را طراحی کن.

### موارد مهم

-   ساخت Category
-   دریافت Categoryها
-   Update
-   Delete
-   Parent Category
-   Child Categories

### Self Relationship

این بخش را دقیق یاد بگیر:

Category → parent\
Category → children

### جلوگیری از ساختارهای خراب

به این حالت‌ها فکر کن:

-   Category والد خودش شود.
-   A والد B و B والد A شود.
-   حذف Parent دارای Child
-   اتصال Category یک User به Category User دیگر، اگر Category شخصی
    باشد.

لازم نیست در نسخه اول تمام مسئله Graph Theory را حل کنی، ولی رفتار سیستم
باید آگاهانه تعریف شود.

**معیار پایان:** hierarchy ساده بدون رابطه خودارجاعی مستقیم یا دسترسی
غیرمجاز کار کند.

------------------------------------------------------------------------

# 20. Task CRUD

عملیات اصلی:

-   Create Task
-   List Tasks
-   Get Task
-   Update Task
-   Delete Task

هر Task باید به User صحیح متصل شود.

`user_id_fk` را صرفاً از ورودی Client اعتماد نکن. مالک Task باید از User
احراز هویت‌شده تعیین شود.

### قابلیت‌های مرحله دوم

بعد از CRUD پایه می‌توانی اضافه کنی:

-   Filter بر اساس completed
-   Filter بر اساس Category
-   Pagination
-   Sort بر اساس created_at
-   جستجو بر اساس title
-   Mark complete/incomplete

**معیار پایان:** User فقط Taskهای مجاز خودش را مدیریت کند.

------------------------------------------------------------------------

# 21. رفتار حذف

برای هر Resource سیاست حذف مشخص کن.

### User

طبق طراحی فعلی:

-   `is_delete`
-   `deleted_at`

هنگام Soft Delete هر دو باید به صورت هماهنگ تغییر کنند.

تصمیم بگیر User حذف‌شده:

-   آیا Login می‌کند؟
-   Tokenهای قبلی او معتبر می‌مانند؟
-   Taskهای او قابل مشاهده‌اند؟
-   امکان Restore وجود دارد؟

### Task و Category

تصمیم بگیر Hard Delete یا Soft Delete لازم است.

### Database Relationships

برای Foreign Keyها درباره این رفتارها تصمیم بگیر:

-   RESTRICT
-   CASCADE
-   SET NULL

**معیار پایان:** هیچ حذف Resource باعث رکوردهای orphan یا رفتار
غیرمنتظره نشود.

------------------------------------------------------------------------

# 22. Refresh Token و Logout

حالا برگرد به `tblTokens`.

اول تفاوت این دو را بفهم:

### Access Token

-   عمر کوتاه
-   برای دسترسی به API

### Refresh Token

-   عمر طولانی‌تر
-   برای دریافت Access Token جدید
-   نیازمند سیاست امن برای نگهداری و revoke شدن

سپس مشخص کن `tblTokens` دقیقاً چه چیزی را ذخیره می‌کند.

### سؤال‌های اجباری

-   آیا خود Refresh Token ذخیره می‌شود یا مقدار Hash شده آن؟
-   expiration چگونه کنترل می‌شود؟
-   Logout چگونه Token/Session را revoke می‌کند؟
-   Logout از یک Device با Logout از همه Deviceها چه تفاوتی دارد؟
-   اگر Refresh Token سرقت شود چه می‌شود؟
-   آیا Token Rotation لازم است؟
-   آیا رکورد Token نیاز به وضعیت revoked یا timestamp مربوط به revoke
    دارد؟
-   آیا شناسه‌ای مثل `jti` برای Token strategy تو مفید است؟

بعد از پاسخ دادن به این سؤال‌ها، Schema `tblTokens` را اصلاح کن و **از
طریق Alembic Migration** تغییر را اعمال کن.

این تغییر عمدی است تا Migration را در یک سناریوی واقعی تمرین کنی.

**معیار پایان:** Logout تعریف دقیق و قابل تست داشته باشد، نه اینکه
Client فقط Token را دور بیندازد و ما اسمش را امنیت بگذاریم.

------------------------------------------------------------------------

# 23. Error Handling

Responseهای خطا را یکدست کن.

موارد:

-   Validation Error
-   Authentication Error
-   Authorization Error
-   Not Found
-   Conflict
-   Database Error
-   Invalid Token
-   Expired Token

HTTP Status Code مناسب را برای هر حالت انتخاب کن و دلیل انتخاب را بدان.

از برگرداندن Stack Trace یا اطلاعات داخلی Database به Client خودداری کن.

**معیار پایان:** خطاها قابل پیش‌بینی، امن و دارای Status Code درست باشند.

------------------------------------------------------------------------

# 24. Transaction Management

سناریوهایی پیدا کن که بیش از یک عملیات Database دارند.

مثلاً:

Register User + Create Profile

اگر عملیات دوم شکست خورد، درباره سرنوشت عملیات اول تصمیم بگیر.

مفاهیم:

-   transaction
-   atomicity
-   rollback
-   commit boundary

**معیار پایان:** عملیات چندمرحله‌ای باعث داده نیمه‌کاره نشوند.

------------------------------------------------------------------------

# 25. API Design

Routeها را مرور کن.

بررسی کن:

-   naming یکدست باشد.
-   HTTP Method درست انتخاب شده باشد.
-   Resourceها درست مدل شده باشند.
-   Status Codeها درست باشند.
-   Responseها قابل پیش‌بینی باشند.
-   business logic بی‌دلیل داخل Router انباشته نشده باشد.

همچنین Swagger/OpenAPI تولیدشده توسط FastAPI را مرتب بررسی کن.

**معیار پایان:** یک Client بدون دیدن سورس بتواند از روی API
documentation نحوه استفاده از API را بفهمد.

------------------------------------------------------------------------

# 26. Logging

Logging حداقلی و مفید اضافه کن.

می‌توانی رخدادهایی مثل این‌ها را ثبت کنی:

-   خطاهای مهم برنامه
-   Login موفق/ناموفق با رعایت امنیت
-   عملیات مدیریتی مهم

هرگز Log نکن:

-   Password
-   JWT کامل
-   Refresh Token
-   Secret Key
-   اطلاعات حساس غیرضروری

**معیار پایان:** Log برای Debug مفید باشد ولی خودش تبدیل به نشت اطلاعات
نشود.

------------------------------------------------------------------------

# 27. Testing

تست را فقط به «آخر پروژه اگر زنده ماندیم» موکول نکن، ولی در این مرحله
Suite را کامل کن.

## Authentication

تست کن:

-   Register موفق
-   Duplicate username
-   Duplicate email
-   Login موفق
-   Password اشتباه
-   User غیرفعال
-   User حذف‌شده
-   Token نامعتبر
-   Token منقضی‌شده
-   Logout
-   Refresh

## Authorization

-   User عادی به Admin endpoint دسترسی نداشته باشد.
-   User A نتواند Task مربوط به User B را بخواند.
-   User A نتواند Task مربوط به User B را Update/Delete کند.

## Profile

-   One-to-One حفظ شود.
-   User نتواند Profile دیگری را تغییر دهد.

## Task

-   Create
-   Read
-   Update
-   Delete
-   Filter
-   Pagination در صورت پیاده‌سازی

## Category

-   CRUD
-   Parent/Child
-   رفتار Delete
-   جلوگیری از parent نامعتبر
-   Ownership در صورت شخصی بودن Category

**معیار پایان:** Happy Path و مهم‌ترین Failure Pathها تست خودکار داشته
باشند.

------------------------------------------------------------------------

# 28. Security Review

قبل از پایان پروژه این Checklist را مرور کن:

-   [ ] Password خام ذخیره نمی‌شود.
-   [ ] Password در Response نیست.
-   [ ] Password/Token در Log نیست.
-   [ ] Secretها داخل Git نیستند.
-   [ ] JWT expiration بررسی می‌شود.
-   [ ] Signature JWT بررسی می‌شود.
-   [ ] User غیرفعال/حذف‌شده سیاست مشخص دارد.
-   [ ] Authorization فقط به Frontend واگذار نشده است.
-   [ ] Ownership در Backend بررسی می‌شود.
-   [ ] Inputها Validation دارند.
-   [ ] ORM Model مستقیماً داده حساس را expose نمی‌کند.
-   [ ] Logout/Revocation تعریف مشخص دارد.
-   [ ] Refresh Token strategy بررسی شده است.
-   [ ] خطاها اطلاعات داخلی سیستم را فاش نمی‌کنند.
-   [ ] Dependencyهای امنیتی به‌روز نگه داشته می‌شوند.

------------------------------------------------------------------------

# 29. Refactoring

بعد از اینکه نسخه اولیه **کار کرد**، Refactor کن.

بررسی کن:

-   آیا Router بیش از حد logic دارد؟
-   آیا Queryهای تکراری داری؟
-   آیا Authentication logic تکرار شده؟
-   آیا Dependencyها درست استفاده شده‌اند؟
-   آیا نام‌گذاری‌ها یکدست هستند؟
-   آیا Model و Schema قاطی شده‌اند؟
-   آیا functionها مسئولیت‌های زیادی دارند؟
-   آیا exception handling تکراری است؟

قانون مهم:

**اول کد صحیح، بعد کد زیبا.**

Refactor کردن چیزی که هنوز کار نمی‌کند فقط تولید خطا با معماری شیک‌تر است.

------------------------------------------------------------------------

# 30. ترتیب اجرای پیشنهادی

پروژه را دقیقاً با این ترتیب جلو ببر:

-   [ ] 1. Requirements و تصمیم‌های معماری
-   [ ] 2. Project setup
-   [ ] 3. Configuration
-   [ ] 4. PostgreSQL
-   [ ] 5. SQLAlchemy setup
-   [ ] 6. User model
-   [ ] 7. Profile model
-   [ ] 8. Category model
-   [ ] 9. Task model
-   [ ] 10. Alembic setup و Migration اولیه
-   [ ] 11. Pydantic schemas
-   [ ] 12. User registration
-   [ ] 13. Password hashing
-   [ ] 14. Login
-   [ ] 15. JWT Access Token
-   [ ] 16. Current User dependency
-   [ ] 17. Role/Ownership Authorization
-   [ ] 18. Profile endpoints
-   [ ] 19. Category CRUD
-   [ ] 20. Task CRUD
-   [ ] 21. Filtering/Pagination
-   [ ] 22. Refresh Token design
-   [ ] 23. اصلاح `tblTokens` و Migration جدید
-   [ ] 24. Refresh flow
-   [ ] 25. Logout/Revocation
-   [ ] 26. Error handling
-   [ ] 27. Transactions
-   [ ] 28. Logging
-   [ ] 29. Automated tests
-   [ ] 30. Security review
-   [ ] 31. Refactoring
-   [ ] 32. Documentation

------------------------------------------------------------------------

# 31. روش کار در هر مرحله

برای اینکه پروژه واقعاً آموزشی بماند، در هر مرحله این چرخه را انجام بده:

### A. Concept

قبل از کدنویسی بتوانی مفهوم را با زبان خودت توضیح بدهی.

### B. Design

مشخص کن قرار است چه چیزی ساخته شود و مسئولیتش چیست.

### C. Implementation

خودت کد را بنویس.

### D. Run

کد را اجرا کن و خروجی واقعی بگیر.

### E. Debug

خطا را ابتدا بخوان و تحلیل کن؛ مستقیم سراغ تغییر تصادفی کد نرو.

### F. Review

کد نوشته‌شده را از نظر:

-   correctness
-   readability
-   security
-   separation of concerns

بررسی کن.

### G. Test

حداقل Happy Path و یک Failure Path مهم را تست کن.

بعد به مرحله بعد برو.

------------------------------------------------------------------------

# 32. Definition of Done پروژه

TodoApp زمانی نسخه آموزشی کامل محسوب می‌شود که:

-   PostgreSQL منبع اصلی داده باشد.
-   تمام تغییرات Schema با Alembic قابل بازسازی باشند.
-   Register امن باشد.
-   Password Hash شود.
-   Login با JWT کار کند.
-   Access Token expiration داشته باشد.
-   Refresh/Logout strategy مشخص و پیاده‌سازی شده باشد.
-   Role-based Authorization وجود داشته باشد.
-   Ownership منابع بررسی شود.
-   User/Profile رابطه One-to-One صحیح داشته باشند.
-   User بتواند Taskهای خودش را CRUD کند.
-   Category و hierarchy آن کار کند.
-   Soft Delete کاربر طبق `is_delete` و `deleted_at` رفتار مشخص داشته
    باشد.
-   Validation با Pydantic انجام شود.
-   خطاها Status Code مناسب داشته باشند.
-   تست‌های مهم Authentication و Authorization وجود داشته باشند.
-   Secretها وارد Repository نشده باشند.
-   README نهایی نحوه Setup و اجرای پروژه را توضیح دهد.

------------------------------------------------------------------------

# 33. نقطه شروع عملی

فعلاً فقط تا پایان این چهار کار جلو برو و بعد وارد SQLAlchemy شو:

1.  Use Caseها و تصمیم‌های باز مرحله صفر را مکتوب کن.
2.  پروژه و Virtual Environment را ایجاد کن.
3.  Dependencyهای اولیه را نصب و ثبت کن.
4.  FastAPI را با یک endpoint ساده اجرا کن.

در این مرحله هنوز Model، JWT، CRUD یا Alembic را با عجله وارد نکن. اگر
پایه پروژه را مرحله‌به‌مرحله بسازی، وقتی به Authentication برسی دقیقاً
می‌دانی هر قطعه چرا وجود دارد.

------------------------------------------------------------------------

## یادداشت پایانی

این Roadmap عمداً بعضی تصمیم‌ها، مخصوصاً Token/Refresh/Logout و جزئیات
Authorization را از قبل حل نکرده است. آن‌ها بخشی از تمرین هستند. هر تصمیم
معماری باید دلیل داشته باشد و تغییر Schema در طول پروژه شکست محسوب
نمی‌شود؛ دقیقاً یکی از دلایلی است که Alembic را یاد می‌گیری.
