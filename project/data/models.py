from enum import Enum

from sqlalchemy import Column, Integer, ForeignKey, String,\
    Boolean, DATE, DECIMAL, Table, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


harvests_employees_asoc_tab = Table('association', Base.metadata,
                                    Column('harvest_id',
                                           ForeignKey('harvests.id'),
                                           primary_key=True),
                                    Column('employee_id',
                                           ForeignKey('employees.id'),
                                           primary_key=True))


class Fruit(str, Enum):
    strawberry = "strawberry"
    cherry = "cherry"
    raspberry = "raspberry"
    apple = "apple"
    blackcurrant = "blackcurrant"
    redcurrant = "redcurrant"
    apricot = "apricot"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    auth_level = Column(Integer, default=1)

    seasons = relationship("Season", back_populates="owner", cascade="all, delete")


class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE)
    owner_id = Column(Integer, ForeignKey("users.id"))

    UniqueConstraint(year, owner_id, name='u_yo')

    owner = relationship("User", back_populates="seasons")

    harvests = relationship("Harvest", back_populates="season", cascade="all, delete")
    employees = relationship("Employee", back_populates="season", cascade="all, delete")
    expenses = relationship("Expense", back_populates="season", cascade="all, delete")

    @property
    def fruits(self):
        return set([h.fruit for h in self.harvests])

    @property
    def harvested_per_fruit(self):
        return {f: sum([h.harvested for h in
                        filter(lambda h: h.fruit == f, self.harvests)]) for f in self.fruits}

    @property
    def value_per_fruit(self):
        return {f: sum([h.harvested * h.price for h in
                filter(lambda h: h.fruit == f, self.harvests)]) for f in self.fruits}

    @property
    def total_harvested_value(self):
        return sum([h.harvested * h.price for h in self.harvests])

    @property
    def total_expenses_value(self):
        return sum([e.amount for e in self.expenses])

    @property
    def total_employee_payments(self):
        return sum(e.total_earnings for e in self.employees)

    @property
    def best_harvest(self):
        best_h: Harvest = max(self.harvests, key=lambda h: h.harvested * h.price, default={})
        return {'id': best_h.id, 'date': best_h.date, 'fruit': best_h.fruit,
                'harvested_value': best_h.harvested * best_h.price} if best_h \
            else {'id': 0, 'date': '', 'fruit': '', 'harvested_value': 0}

    @property
    def best_employee(self):
        best_e: Employee = max(self.employees, key=lambda e: e.total_harvested, default={})
        return {'id': best_e.id, 'name': best_e.name, 'total_harvested': best_e.total_harvested} if best_e \
            else {'id': 0, 'name': '', 'total_harvested': 0}

    @property
    def best_employees_per_fruit(self):
        best_emp_per_fruit = {}
        for f in self.fruits:
            best_emp: Employee = max(self.employees, key=lambda e: e.harvested_per_fruit[f], default={})
            best_emp_per_fruit[f] = {'id': best_emp.id, 'name': best_emp.name,
                                     'harvested': best_emp.harvested_per_fruit[f]} if best_emp else {'id': 0, 'name': ''}
        return best_emp_per_fruit


class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    fruit = Column(String, nullable=False)
    harvested = Column(DECIMAL(5, 1), nullable=False)
    date = Column(DATE, nullable=False)
    price = Column(DECIMAL(5, 1), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    UniqueConstraint(date, fruit, name='u_df')

    season = relationship("Season", back_populates="harvests")

    employees = relationship("Employee",
                             secondary=harvests_employees_asoc_tab,
                             back_populates="harvests")

    workdays = relationship("Workday", back_populates="harvest", cascade="all, delete")

    @property
    def harvested_per_employee(self):
        return [{"id": w.employee.id,
                 "name": w.employee.name,
                 "harvested": round(float(w.harvested), 2),
                 "pay_per_kg": round(float(w.pay_per_kg), 2),
                 "earned": round(float(w.harvested * w.pay_per_kg), 2)} for w in self.workdays]

    @property
    def harvested_max(self):
        return max([w.harvested for w in self.workdays], default=0)

    @property
    def best_employee(self):
        return next((emp
                     for emp
                     in self.harvested_per_employee
                     if emp['harvested'] == self.harvested_max), {})

    @property
    def total_profits(self):
        return self.harvested * self.price

    @property
    def harvested_by_employees(self):
        return sum([w.harvested for w in self.workdays])

    @property
    def avg_pay_per_kg(self):
        return sum([w.harvested * w.pay_per_kg for w in self.workdays]) / sum([w.harvested for w in self.workdays])

    @property
    def self_harvested(self):
        return self.harvested - self.harvested_by_employees

    @property
    def self_harvested_profits(self):
        return self.self_harvested * self.price

    @property
    def net_profit(self):
        return self.harvested * self.price - self.harvested_by_employees * self.avg_pay_per_kg


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    date = Column(DATE, nullable=False)
    amount = Column(DECIMAL(6, 1), nullable=False)
    season_id = Column(ForeignKey("seasons.id"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    season = relationship("Season", back_populates="expenses")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE)

    season = relationship("Season", back_populates="employees")

    harvests = relationship("Harvest",
                            secondary=harvests_employees_asoc_tab,
                            back_populates="employees")

    workdays = relationship("Workday", back_populates="employee", cascade="all, delete")

    @property
    def fruits(self):
        return set([w.fruit for w in self.workdays])

    @property
    def harvested_per_fruit(self):
        return {f: sum([w.harvested for w in
                        filter(lambda w: w.fruit == f, self.workdays)]) for f in self.fruits}

    @property
    def total_harvested(self):
        return sum(w.harvested for w in self.workdays)

    @property
    def earned_per_fruit(self):
        return {f: sum([w.harvested*w.pay_per_kg for w in
                        filter(lambda w: w.fruit == f, self.workdays)]) for f in self.fruits}

    @property
    def total_earnings(self):
        return sum(self.earned_per_fruit.values())

    @property
    def harvests_history(self):
        h_history = [{"id": w.harvest.id,
                      "date": w.harvest.date,
                      "fruit": w.fruit,
                      "harvested": w.harvested,
                      "pay_per_kg": w.pay_per_kg,
                      "earned": w.harvested * w.pay_per_kg} for w in self.workdays]
        return h_history

    @property
    def best_harvest(self):
        max_harvested = max([w.harvested for w in self.workdays], default=0)
        return next((har
                     for har
                     in self.harvests_history
                     if har['harvested'] == max_harvested), {})


class Workday(Base):
    __tablename__ = "workdays"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    harvest_id = Column(Integer, ForeignKey("harvests.id"))
    harvested = Column(DECIMAL(5, 1))
    pay_per_kg = Column(DECIMAL(5, 1))
    fruit = Column(String(30), nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    employee = relationship("Employee", back_populates="workdays")
    harvest = relationship("Harvest", back_populates="workdays")
