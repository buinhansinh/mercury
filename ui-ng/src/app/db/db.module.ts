import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { OfferService } from "./offer.service";
import { UserService } from "./user.service";
import { ContactService } from "./contact.service";
import { GroupService } from "./group.service";
import { HttpClientModule } from "@angular/common/http";

@NgModule({
  imports: [CommonModule, HttpClientModule],
  providers: [UserService, OfferService, ContactService, GroupService],
  declarations: []
})
export class DbModule {}
