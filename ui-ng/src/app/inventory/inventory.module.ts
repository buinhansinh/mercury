import { NgModule } from "@angular/core";
import { OrderTransferFormComponent } from "./order-transfer-form/order-transfer-form.component";
import { InventoryComponent } from "./inventory.component";
import { InventoryRoutingModule } from "./inventory-routing.module";
import { AppCommonModule } from "../app-common/app-common.module";
import { LocationTransferFormComponent } from "./location-transfer-form/location-transfer-form.component";
import { LocationAdjustmentFormComponent } from "./location-adjustment-form/location-adjustment-form.component";

@NgModule({
  imports: [AppCommonModule, InventoryRoutingModule],
  declarations: [
    OrderTransferFormComponent,
    InventoryComponent,
    LocationTransferFormComponent,
    LocationAdjustmentFormComponent
  ]
})
export class InventoryModule {}
