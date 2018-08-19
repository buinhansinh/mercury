import { NgModule } from "@angular/core";
import { OrderItemComponent } from "./order-item/order-item.component";
import { InventoryService } from "../db/inventory.service";
import { OrderService } from "../db/order.service";
// import { OrderServiceComponent } from './order-service/order-service.component';
import { AppCommonModule } from "../app-common/app-common.module";
import { OrderFormComponent } from "./order-form/order-form.component";
import { OrderPricingInfoComponent } from "./order-pricing-info/order-pricing-info.component";
import { OrderStockInfoComponent } from "./order-stock-info/order-stock-info.component";

@NgModule({
  imports: [AppCommonModule],
  declarations: [
    OrderItemComponent,
    // OrderServiceComponent,
    OrderFormComponent,
    OrderPricingInfoComponent,
    OrderStockInfoComponent
  ],
  providers: [OrderService, InventoryService],
  exports: [OrderFormComponent],
  entryComponents: [OrderPricingInfoComponent, OrderStockInfoComponent]
})
export class OrderModule {}
