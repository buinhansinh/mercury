import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";

import { BrowserModule } from "@angular/platform-browser";

import { BrowserAnimationsModule } from "@angular/platform-browser/animations";

import {
  // nvaigation
  MatToolbarModule,
  MatSidenavModule,
  MatMenuModule,

  // layout
  MatExpansionModule,
  MatListModule,
  MatCardModule,
  MatTabsModule,

  // buttons
  MatIconModule,
  MatButtonModule,
  MatChipsModule,
  MatBadgeModule,

  // forms
  MatInputModule,
  MatAutocompleteModule,
  MatCheckboxModule,

  // popups
  MatSnackBarModule,
  MatDialogModule,
  ErrorStateMatcher,
  ShowOnDirtyErrorStateMatcher,
  MatDatepickerModule,
  MatTableModule,
  MatNativeDateModule,
  MatPaginatorModule,
  MatSortModule
} from "@angular/material";
import { MatFormFieldModule } from "@angular/material/form-field";
import { OfferPickerComponent } from "./offer-picker/offer-picker.component";
import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { SelectOnFocusDirective } from "./select-on-focus.directive";
import { ContactPickerComponent } from "./contact-picker/contact-picker.component";

const ngModules: any = [
  CommonModule,
  BrowserModule,
  BrowserAnimationsModule,
  FormsModule,
  ReactiveFormsModule
];

const materialModules: any = [
  // navigation
  MatToolbarModule,
  MatSidenavModule,
  MatMenuModule,

  // layout
  MatExpansionModule,
  MatListModule,
  MatCardModule,
  MatTabsModule,

  // modals
  MatSnackBarModule,
  MatDialogModule,

  // buttons and indicators
  MatIconModule,
  MatButtonModule,
  MatChipsModule,
  MatBadgeModule,

  // forms
  MatCheckboxModule,
  MatInputModule,
  MatAutocompleteModule,
  MatFormFieldModule,
  MatDatepickerModule,
  MatNativeDateModule,

  // tables
  MatTableModule,
  MatPaginatorModule,
  MatSortModule
];

const commonComponents: any = [
  ContactPickerComponent,
  OfferPickerComponent,
  SelectOnFocusDirective
];

const declarations_ = [].concat(commonComponents);
const imports_ = [].concat(ngModules).concat(materialModules);
const exports_ = []
  .concat(ngModules)
  .concat(materialModules)
  .concat(commonComponents);

@NgModule({
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  declarations: declarations_,
  imports: imports_,
  exports: exports_,
  providers: [
    { provide: ErrorStateMatcher, useClass: ShowOnDirtyErrorStateMatcher }
  ]
})
export class AppCommonModule {}
