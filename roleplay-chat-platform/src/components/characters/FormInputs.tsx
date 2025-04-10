"use client";

interface InputFieldProps {
  id: string;
  label: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  error?: string;
  required?: boolean;
  className?: string;
  maxLength?: number;
}

export function InputField({
  id,
  label,
  type = "text",
  value,
  onChange,
  placeholder,
  error,
  required = false,
  className = "",
  maxLength,
}: InputFieldProps) {
  return (
    <div className={`mb-4 ${className}`}>
      <label htmlFor={id} className="block text-sm font-medium mb-1 text-slate-300">
        {label} {required && <span className="text-red-400">*</span>}
      </label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        maxLength={maxLength}
        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white"
      />
      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  );
}

interface TextAreaFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  error?: string;
  required?: boolean;
  className?: string;
  rows?: number;
  maxLength?: number;
}

export function TextAreaField({
  id,
  label,
  value,
  onChange,
  placeholder,
  error,
  required = false,
  className = "",
  rows = 5,
  maxLength,
}: TextAreaFieldProps) {
  return (
    <div className={`mb-4 ${className}`}>
      <label htmlFor={id} className="block text-sm font-medium mb-1 text-slate-300">
        {label} {required && <span className="text-red-400">*</span>}
      </label>
      <textarea
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        rows={rows}
        maxLength={maxLength}
        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white"
      />
      {maxLength && (
        <div className="flex justify-end mt-1">
          <span className={`text-xs ${value.length > maxLength * 0.9 ? "text-red-400" : "text-slate-500"}`}>
            {value.length}/{maxLength}
          </span>
        </div>
      )}
      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  );
}

interface SelectFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: { value: string; label: string }[];
  error?: string;
  required?: boolean;
  className?: string;
  placeholder?: string;
}

export function SelectField({
  id,
  label,
  value,
  onChange,
  options,
  error,
  required = false,
  className = "",
  placeholder = "Select an option",
}: SelectFieldProps) {
  return (
    <div className={`mb-4 ${className}`}>
      <label htmlFor={id} className="block text-sm font-medium mb-1 text-slate-300">
        {label} {required && <span className="text-red-400">*</span>}
      </label>
      <select
        id={id}
        value={value}
        onChange={onChange}
        required={required}
        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-white"
      >
        <option value="" disabled>
          {placeholder}
        </option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  );
}

interface CheckboxFieldProps {
  id: string;
  label: React.ReactNode;
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  className?: string;
}

export function CheckboxField({
  id,
  label,
  checked,
  onChange,
  error,
  className = "",
}: CheckboxFieldProps) {
  return (
    <div className={`mb-4 ${className}`}>
      <div className="flex items-start">
        <div className="flex items-center h-5">
          <input
            id={id}
            type="checkbox"
            checked={checked}
            onChange={onChange}
            className="h-4 w-4 text-blue-500 border-slate-600 rounded focus:ring-blue-500"
          />
        </div>
        <div className="ml-3 text-sm">
          <label htmlFor={id} className="text-slate-300">
            {label}
          </label>
          {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
        </div>
      </div>
    </div>
  );
}

interface RadioGroupProps {
  id: string;
  legend: string;
  options: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
  error?: string;
  required?: boolean;
  className?: string;
}

export function RadioGroup({
  id,
  legend,
  options,
  value,
  onChange,
  error,
  required = false,
  className = "",
}: RadioGroupProps) {
  return (
    <div className={`mb-4 ${className}`}>
      <fieldset>
        <legend className="block text-sm font-medium mb-2 text-slate-300">
          {legend} {required && <span className="text-red-400">*</span>}
        </legend>
        <div className="space-y-2">
          {options.map((option) => (
            <div key={option.value} className="flex items-center">
              <input
                id={`${id}-${option.value}`}
                type="radio"
                checked={value === option.value}
                onChange={() => onChange(option.value)}
                className="h-4 w-4 text-blue-500 border-slate-600 focus:ring-blue-500"
              />
              <label
                htmlFor={`${id}-${option.value}`}
                className="ml-3 block text-sm text-slate-300"
              >
                {option.label}
              </label>
            </div>
          ))}
        </div>
        {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
      </fieldset>
    </div>
  );
}

interface KinkRatingProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

export function KinkRating({
  id,
  label,
  value,
  onChange,
  className = "",
}: KinkRatingProps) {
  const ratings = [
    { value: "fave", label: "Favorite", color: "bg-green-500" },
    { value: "yes", label: "Yes", color: "bg-blue-500" },
    { value: "maybe", label: "Maybe", color: "bg-yellow-500" },
    { value: "no", label: "No", color: "bg-red-500" },
  ];

  return (
    <div className={`flex items-center mb-3 p-3 bg-slate-800 border border-slate-700 rounded-md ${className}`}>
      <div className="flex-grow">
        <span className="text-sm font-medium text-slate-200">{label}</span>
      </div>
      <div className="flex space-x-2">
        {ratings.map((rating) => (
          <button
            key={rating.value}
            type="button"
            onClick={() => onChange(rating.value)}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
              value === rating.value
                ? `${rating.color} text-white`
                : "bg-slate-700 text-slate-400 hover:bg-slate-600"
            }`}
          >
            {rating.label}
          </button>
        ))}
      </div>
    </div>
  );
}

interface ImageUploadProps {
  id: string;
  label: string;
  onChange: (file: File | null) => void;
  previewUrl: string | null;
  error?: string;
  required?: boolean;
  className?: string;
  accept?: string;
}

export function ImageUpload({
  id,
  label,
  onChange,
  previewUrl,
  error,
  required = false,
  className = "",
  accept = "image/*",
}: ImageUploadProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    onChange(file);
  };

  return (
    <div className={`mb-4 ${className}`}>
      <label htmlFor={id} className="block text-sm font-medium mb-1 text-slate-300">
        {label} {required && <span className="text-red-400">*</span>}
      </label>
      <div className="mt-2">
        {previewUrl ? (
          <div className="mb-3 relative w-full max-w-[200px] rounded-md overflow-hidden group">
            <img
              src={previewUrl}
              alt="Preview"
              className="w-full h-auto object-cover rounded-md"
            />
            <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <button
                type="button"
                onClick={() => onChange(null)}
                className="bg-red-500 text-white p-1 rounded-full hover:bg-red-600 transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>
        ) : (
          <div className="flex justify-center px-6 pt-5 pb-6 border-2 border-dashed border-slate-600 rounded-md hover:border-slate-500 transition-colors">
            <div className="space-y-1 text-center">
              <svg
                className="mx-auto h-12 w-12 text-slate-500"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="flex text-sm text-slate-400">
                <label
                  htmlFor={id}
                  className="relative cursor-pointer bg-slate-800 rounded-md font-medium text-blue-400 hover:text-blue-300 focus-within:outline-none"
                >
                  <span>Upload a file</span>
                  <input
                    id={id}
                    name={id}
                    type="file"
                    accept={accept}
                    className="sr-only"
                    onChange={handleChange}
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-slate-500">PNG, JPG, GIF up to 10MB</p>
            </div>
          </div>
        )}
      </div>
      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  );
}
