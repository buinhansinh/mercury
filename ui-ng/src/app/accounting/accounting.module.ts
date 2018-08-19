import { NgModule } from "@angular/core";
import { AccountingComponent } from "./accounting.component";
import { PaymentFormComponent } from "./payment-form/payment-form.component";
import { PaymentAllocationComponent } from "./payment-allocation/payment-allocation.component";
import { ExpenseFormComponent } from "./expense-form/expense-form.component";
import { RefundFormComponent } from "./refund-form/refund-form.component";
import { AppCommonModule } from "../app-common/app-common.module";
import { AccountingRoutingModule } from "./accounting-routing.module";
import { InvoicesComponent } from "./invoices/invoices.component";
import { DiscountFormComponent } from "./discount-form/discount-form.component";
import { PaymentAllocationPickerComponent } from "./payment-allocation-picker/payment-allocation-picker.component";

@NgModule({
  imports: [AppCommonModule, AccountingRoutingModule],
  declarations: [
    AccountingComponent,
    PaymentFormComponent,
    PaymentAllocationComponent,
    ExpenseFormComponent,
    RefundFormComponent,
    InvoicesComponent,
    DiscountFormComponent,
    PaymentAllocationPickerComponent
  ],
  entryComponents: [DiscountFormComponent, PaymentAllocationPickerComponent]
})
export class AccountingModule {}
