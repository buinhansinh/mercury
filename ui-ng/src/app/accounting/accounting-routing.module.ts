import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { AccountingComponent } from "./accounting.component";
import { PaymentFormComponent } from "./payment-form/payment-form.component";
import { RefundFormComponent } from "./refund-form/refund-form.component";
import { PaymentAllocationComponent } from "./payment-allocation/payment-allocation.component";
import { ExpenseFormComponent } from "./expense-form/expense-form.component";
import { InvoicesComponent } from "./invoices/invoices.component";

const routes: Routes = [
  {
    path: "accounting",
    component: AccountingComponent,
    children: [
      {
        path: "receivables",
        component: InvoicesComponent
      },
      {
        path: "payables",
        component: InvoicesComponent
      },
      {
        path: "payment",
        component: PaymentFormComponent
      },
      {
        path: "payment/:id",
        component: PaymentFormComponent
      },
      {
        path: "payment/:id/refund",
        component: RefundFormComponent
      },
      {
        path: "disbursement",
        component: PaymentFormComponent
      },
      {
        path: "disbursement/:id",
        component: PaymentFormComponent
      },
      {
        path: "disbursement/:id/refund",
        component: RefundFormComponent
      },
      {
        path: "payment/:id/allocation",
        component: PaymentAllocationComponent
      },
      {
        path: "disbursement/:id/allocation",
        component: PaymentAllocationComponent
      },
      {
        path: "expense",
        component: ExpenseFormComponent
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AccountingRoutingModule {}
