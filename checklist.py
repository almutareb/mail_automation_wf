from dataclasses import dataclass
from datetime import datetime


@dataclass
class Checklist:
    insured_party_name: str = None
    insured_party_address: str = None
    policy_number: str = None
    incident_location: str = None
    incident_date: datetime = None


    def get_pending_items(self) -> list[str]:
        """ Returns the checklist items that are empty/None """
        return [field for field, value in self.__dict__.items() if value is None]


if __name__ == '__main__':
    # Create an empty checklist
    checklist = Checklist()
    
    # Update an item in the checklist
    checklist.incident_date = datetime(year=2023,month=3, day=12, hour=10, minute=30)
    
    # Get items that are pending
    pending_items = checklist.get_pending_items()
    print(f'{pending_items = }')
    
    # Initialize a checklist with values
    checklist2 = Checklist(insured_party_name='James', 
                           insured_party_address='London', 
                           policy_number='007', 
                           incident_location='Russia', 
                           incident_date=datetime(year=2000, month=4, day=1))
    print(f"{checklist2.__dict__ = }")
    print(f"{checklist2.incident_location = }")
