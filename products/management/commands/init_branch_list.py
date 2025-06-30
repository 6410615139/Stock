from django.core.management.base import BaseCommand
from products.models import Branch, Supplier

DEFAULT_BRANCHES = [
    "สำนักงานใหญ่",
    "ลาซาล",
    "รังสิต",
    "ฟอร์จูน",
    "ติวานนท์",
    "เชียงใหม่",
    "อุดรธานี",
    "ขอนแก่น",
    "อุบลราชธานี",
    "โคราช",
    "ศรีราชา",
    "อยุธยา",
    "หัวหิน",
    "สุราษฎร์ธานี",
    "หาดใหญ่",
    "เชียงใหม่ (ไผ่)",
    "ภายใน",
]

DEFAULT_SUPPLIER = [
    "อื่นๆ"
]

class Command(BaseCommand):
    help = "Initialize branch list if none exists"

    def handle(self, *args, **kwargs):
        if Branch.objects.exists():
            self.stdout.write(self.style.NOTICE("🔹 Branch list already exists. No changes made."))
            return

        for name in DEFAULT_BRANCHES:
            Branch.objects.create(name=name)
            self.stdout.write(f"✅ Created branch: {name}")

        for name in DEFAULT_SUPPLIER:
            Supplier.objects.create(name=name)
            self.stdout.write(f"✅ Created supplier: {name}")

        self.stdout.write(self.style.SUCCESS("🎉 Default objects initialized successfully."))
