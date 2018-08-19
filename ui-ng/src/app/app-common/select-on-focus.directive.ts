import { Directive, ElementRef, HostListener } from "@angular/core";

@Directive({
  selector: "[appSelectOnFocus]"
})
export class SelectOnFocusDirective {
  constructor(private el: ElementRef) {}

  @HostListener("focus")
  onfocus() {
    this.el.nativeElement.select();
  }
}
