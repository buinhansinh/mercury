import { NgModule } from "@angular/core";
import { AppCommonModule } from "../app-common/app-common.module";
import { AdminRoutingModule } from "./admin-routing.module";
import { AdminComponent } from "./admin.component";
import { UserComponent } from "./user/user.component";
import { UsernameExistsDirective } from "./user/username-exists.directive";

@NgModule({
  imports: [AppCommonModule, AdminRoutingModule],
  providers: [],
  declarations: [AdminComponent, UserComponent, UsernameExistsDirective]
})
export class AdminModule {}
