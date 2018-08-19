import { NgModule } from "@angular/core";
import { ContactComponent } from "./contact/contact.component";
import { ContactFormComponent } from "./contact-form/contact-form.component";
import { AppCommonModule } from "../app-common/app-common.module";
import { ProductFormComponent } from "./product-form/product-form.component";
import { ServiceFormComponent } from "./service-form/service-form.component";

@NgModule({
  imports: [AppCommonModule],
  entryComponents: [
    ContactFormComponent,
    ProductFormComponent,
    ServiceFormComponent
  ],
  declarations: [
    ContactComponent,
    ContactFormComponent,
    ProductFormComponent,
    ServiceFormComponent
  ],
  exports: []
})
export class CompanyModule {}
