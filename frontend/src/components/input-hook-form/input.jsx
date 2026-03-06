import "./input.css";
import { useFormContext } from "react-hook-form";

export default function Input({ name, className = "", ...rest }) {
  const {
    register,
    formState: { errors },
  } = useFormContext();

  const error = errors?.[name]?.message;

  return (
    <div className="input-wrapper">

      <input
        id={name}
        className={`input ${error ? "input-error" : ""} ${className}`}
        {...rest}        
        {...register(name)} 
      />
    </div>
  );
}