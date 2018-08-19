import { Directive, Input } from "@angular/core";
import { UserService } from "../../db/user.service";
import {
  Validator,
  AsyncValidator,
  NG_ASYNC_VALIDATORS,
  AbstractControl,
  ValidationErrors
} from "@angular/forms";
import { Observable, of } from "rxjs";
import { map } from "rxjs/operators";

@Directive({
  selector: "[appUsernameExists]",
  providers: [
    {
      provide: NG_ASYNC_VALIDATORS,
      useExisting: UsernameExistsDirective,
      multi: true
    }
  ]
})
export class UsernameExistsDirective implements AsyncValidator {
  @Input("appUsernameExists")
  formerName: string;

  constructor(private userService: UserService) {}

  validate(
    c: AbstractControl
  ): Promise<ValidationErrors | null> | Observable<ValidationErrors | null> {
    return this.userService.exists(c.value).pipe(
      map(exists => {
        return exists && c.value !== this.formerName
          ? { usernameExists: "username already exists" }
          : null;
      })
    );
  }
}
