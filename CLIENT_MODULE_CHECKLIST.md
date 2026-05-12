# Client Module Checklist

## Payment MVP

- [x] Add client payment submission route
- [x] Create client payment submission page
- [x] Show live GCash QR and instructions
- [x] Accept reference number from client
- [x] Accept optional screenshot upload
- [x] Save submitted proof against appointment
- [x] Surface payment status in `My Appointments`
- [x] Sync admin payment verification to appointment payment status
- [x] Handle missing screenshot safely in admin payment list

## Follow-up Cleanup

- [ ] Normalize appointment status names with product wording (`Approved` vs `Confirmed`, `Rejected` vs `Cancelled`)
- [ ] Protect remaining admin views with consistent staff-only guards
- [ ] Remove legacy duplicate scheduling/payment code paths from `main/views.py`
- [ ] Add tests for booking and payment flows
