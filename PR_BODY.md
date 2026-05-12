## Summary

This PR improves the client booking and payment experience, fixes broken admin appointment actions, refreshes the appointment requests UI, and hardens image handling for production deployments with Cloudinary.

## What changed

- Fixed the duplicate booking flow so the active appointment booking view uses the correct template and current `Appointment` fields
- Prevented booking submission when a client has no pets or when no slots are available
- Added clearer validation feedback on the client booking page
- Fixed appointment slot/date handling to use Django's local timezone consistently
- Added staff-only protection to the appointment requests page
- Added real backend routes for approving and cancelling appointment requests
- Updated the approve action to create a linked `MedicalRecord` only when appropriate for `Check-up` and `Consultation`
- Refreshed the admin appointment requests page styling and connected its dedicated CSS
- Added a client GCash payment submission page per appointment
- Exposed payment status and `Pay Now` / `Update Payment` actions inside `My Appointments`
- Made payment screenshots optional and added the migration for that schema change
- Fixed admin payment verification to update the current `Appointment.payment_status` field
- Made the admin payments page handle missing screenshots safely
- Added a checklist file to track completed MVP work and remaining cleanup items
- Wired media storage to switch to Cloudinary automatically when `CLOUDINARY_URL` is present
- Added `.env.example` with the expected `CLOUDINARY_URL` format
- Updated QR code generation to save through Django `default_storage` so production storage works with Cloudinary
- Removed the stale service upload override that was preventing service images from being saved correctly

## Files of note

- `main/views.py`
- `main/urls.py`
- `main/models.py`
- `main/templates/clients/payment_submission.html`
- `main/templates/clients/my_appointments.html`
- `main/templates/admin/appointment_requests.html`
- `main/templates/admin/payments_admin.html`
- `main/static/css/admin/appointment_list.css`
- `main/static/css/clients/payment_submission.css`
- `MFC_PETCARE_SYSTEM/settings.py`
- `main/migrations/0009_alter_payment_screenshot.py`
- `CLIENT_MODULE_CHECKLIST.md`
- `.env.example`

## Validation

- Ran `python manage.py check`
- Ran `python manage.py migrate`
- Ran `python manage.py test main.tests` and confirmed the repo currently has no tests in that module

## Follow-ups

- Normalize appointment status naming with product wording
- Protect the rest of the admin views consistently with staff-only guards
- Remove more legacy duplicate code paths in `main/views.py`
- Add automated tests for booking, payment, and admin appointment actions
