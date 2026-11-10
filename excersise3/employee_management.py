import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Employee:
    employee_id: str
    name: str
    department: str
    salary: float

    def __post_init__(self):
        self.employee_id = self.employee_id.strip()
        self.name = self.name.strip()
        self.department = self.department.strip()
        if not self.employee_id:
            raise ValueError("Employee ID cannot be empty.")
        if not self.name:
            raise ValueError("Name cannot be empty.")
        if not self.department:
            raise ValueError("Department cannot be empty.")
        if self.salary < 0:
            raise ValueError("Salary cannot be negative.")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            employee_id=str(data["employee_id"]),
            name=str(data["name"]),
            department=str(data["department"]),
            salary=float(data["salary"]),
        )


class EmployeeManager:
    def __init__(self, storage_path="employees.json"):
        self.storage_path = Path(storage_path)
        self.employees = {}
        self.load()

    def load(self):
        if not self.storage_path.exists():
            return

        try:
            with self.storage_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("Employee data must be a JSON list.")

            employees = {}
            for record in data:
                employee = Employee.from_dict(record)
                if employee.employee_id in employees:
                    raise ValueError(
                        f"Duplicate employee ID in JSON file: {employee.employee_id}"
                    )
                employees[employee.employee_id] = employee
            self.employees = employees
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ValueError(f"Could not read employee data: {error}") from error

    def _save(self, employees):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(
                [employee.to_dict() for employee in employees.values()],
                file,
                indent=4,
            )

    def add_employee(self, employee):
        if employee.employee_id in self.employees:
            raise ValueError(f"Employee ID already exists: {employee.employee_id}")
        updated = {**self.employees, employee.employee_id: employee}
        self._save(updated)
        self.employees = updated

    def update_employee(
        self, employee_id, *, name=None, department=None, salary=None
    ):
        employee_id = employee_id.strip()
        if employee_id not in self.employees:
            raise KeyError(f"Employee not found: {employee_id}")

        current = self.employees[employee_id]
        updated_employee = Employee(
            employee_id=employee_id,
            name=current.name if name is None else name,
            department=current.department if department is None else department,
            salary=current.salary if salary is None else salary,
        )
        updated = {**self.employees, employee_id: updated_employee}
        self._save(updated)
        self.employees = updated

    def delete_employee(self, employee_id):
        employee_id = employee_id.strip()
        if employee_id not in self.employees:
            raise KeyError(f"Employee not found: {employee_id}")
        updated = {
            key: employee
            for key, employee in self.employees.items()
            if key != employee_id
        }
        self._save(updated)
        self.employees = updated

    def get_employee(self, employee_id):
        employee_id = employee_id.strip()
        if employee_id not in self.employees:
            raise KeyError(f"Employee not found: {employee_id}")
        return self.employees[employee_id]

    def get_all_employees(self):
        return sorted(self.employees.values(), key=lambda employee: employee.employee_id)


def display_employee(employee):
    print(
        f"ID: {employee.employee_id} | Name: {employee.name} | "
        f"Department: {employee.department} | Salary: {employee.salary:.2f}"
    )


def run():
    try:
        manager = EmployeeManager()
    except (OSError, ValueError) as error:
        print(f"Unable to load employee records: {error}")
        return

    actions = {
        "1": "Add employee",
        "2": "Update employee",
        "3": "Delete employee",
        "4": "View employee",
        "5": "View all employees",
        "6": "Exit",
    }

    while True:
        print("\nEmployee Management")
        for choice, label in actions.items():
            print(f"{choice}. {label}")

        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                employee = Employee(
                    employee_id=input("Employee ID: "),
                    name=input("Name: "),
                    department=input("Department: "),
                    salary=float(input("Salary: ")),
                )
                manager.add_employee(employee)
                print("Employee added.")
            elif choice == "2":
                employee_id = input("Employee ID to update: ")
                current = manager.get_employee(employee_id)
                name = input(f"Name [{current.name}]: ").strip() or current.name
                department = (
                    input(f"Department [{current.department}]: ").strip()
                    or current.department
                )
                salary_input = input(f"Salary [{current.salary:.2f}]: ").strip()
                salary = float(salary_input) if salary_input else current.salary
                manager.update_employee(
                    employee_id, name=name, department=department, salary=salary
                )
                print("Employee updated.")
            elif choice == "3":
                manager.delete_employee(input("Employee ID to delete: "))
                print("Employee deleted.")
            elif choice == "4":
                display_employee(manager.get_employee(input("Employee ID: ")))
            elif choice == "5":
                employees = manager.get_all_employees()
                if not employees:
                    print("No employee records found.")
                for employee in employees:
                    display_employee(employee)
            elif choice == "6":
                print("Goodbye.")
                break
            else:
                print("Please choose a valid option (1-6).")
        except (ValueError, KeyError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    run()
