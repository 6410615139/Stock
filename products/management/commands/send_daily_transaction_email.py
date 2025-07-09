from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils.timezone import now

from products.models import Transaction, Import

import pandas as pd
from io import BytesIO


class Command(BaseCommand):
    help = "Send daily Transaction and Import reports to Gmail"

    def handle(self, *args, **kwargs):
        today = now().date()

        # === Get today's data ===
        transfers = Transaction.objects.filter(created_at__date=today)
        imports = Import.objects.filter(created_at__date=today)

        if not transfers.exists() and not imports.exists():
            self.stdout.write("No transactions or imports today.")
            return

        # === Create summary ===
        summary_lines = [
            f"📦 Total Transfers: {transfers.count()}",
            f"🛬 Total Imports: {imports.count()}",
            "",
            "See attached Excel files for details."
        ]
        body = "\n".join(summary_lines)

        # === Convert to DataFrames ===
        transfer_df = pd.DataFrame([tx.to_excel_row() for tx in transfers])
        import_df = pd.DataFrame([imp.to_excel_row() for imp in imports])

        # === Write Excel files to memory ===
        transfer_buffer = BytesIO()
        import_buffer = BytesIO()

        transfer_df.to_excel(transfer_buffer, index=False)
        import_df.to_excel(import_buffer, index=False)

        # Reset pointer to start
        transfer_buffer.seek(0)
        import_buffer.seek(0)

        # === Send Email ===
        email = EmailMessage(
            subject=f"Daily Stock Reports - {today.strftime('%Y-%m-%d')}",
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=["your_email@gmail.com"],  # change to recipient
        )

        if not transfer_df.empty:
            email.attach("branch_transfers.xlsx", transfer_buffer.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        if not import_df.empty:
            email.attach("stock_imports.xlsx", import_buffer.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        email.send()
        self.stdout.write("✅ Email sent with Excel attachments and summary.")
