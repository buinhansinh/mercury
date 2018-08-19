import { NgModule } from "@angular/core";
import { ManagementComponent } from "./management.component";
import { UserFormComponent } from "./user-form/user-form.component";
import { GroupFormComponent } from "./group-form/group-form.component";
import { LocationFormComponent } from "./location-form/location-form.component";
import { UsersComponent } from "./users/users.component";
import { GroupsComponent } from "./groups/groups.component";
import { LocationsComponent } from "./locations/locations.component";
import { AppCommonModule } from "../app-common/app-common.module";
import { ManagementRoutingModule } from "./management-routing.module";
import { ReportsComponent } from "./reports/reports.component";

@NgModule({
  imports: [AppCommonModule, ManagementRoutingModule],
  declarations: [
    ManagementComponent,
    UserFormComponent,
    GroupFormComponent,
    LocationFormComponent,
    UsersComponent,
    GroupsComponent,
    LocationsComponent,
    ReportsComponent
  ]
})
export class ManagementModule {}
