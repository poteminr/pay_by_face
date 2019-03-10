pragma solidity ^0.5.2;
contract Registrar {
    address public owner;
    string  public str="";
    mapping (address=>string)  AddPhone;
    mapping (address=>string)  DellPhone;
    mapping (string => address)  PhoneToAddress;
    mapping (address =>string)  AddressToPhone;
    struct Confirmed
    {
        address add;
        string phone;
    }
    Confirmed[] Add_lists;
    Confirmed[] Del_lists;
    uint NowAdd ;
    uint NowDel ;

    constructor() public {
        owner = msg.sender;
        NowAdd=0;
        NowDel=0;
    }
    event RegistrationRequest(address indexed sender);
    event UnregistrationRequest(address indexed sender);
    event UnregistrationCanceled(address indexed sender);
    event RegistrationCanceled(address indexed sender);


    function Compare(string memory a, string memory b) public pure returns(bool)
    {
        return keccak256(abi.encodePacked(a))==keccak256(abi.encodePacked(b));
    }
    function RegistrationPhone(string memory _val) public
    {
        require(PhoneValid(_val));
        AddPhone[msg.sender] = _val;
        Add_lists.push(Confirmed(msg.sender, _val));
        emit RegistrationRequest(msg.sender);
    }
    function UnregistrationPhone() public
    {
        require(!Compare(AddressToPhone[msg.sender],str));
        DellPhone[msg.sender] = AddressToPhone[msg.sender];
        Del_lists.push(Confirmed(msg.sender, AddressToPhone[msg.sender]));
        emit UnregistrationRequest(msg.sender);
    }
    function Cancel() public
    {
        if (!Compare(AddressToPhone[msg.sender],str) && !Compare(DellPhone[msg.sender],str))
        {
            delete(DellPhone[msg.sender]);
            emit UnregistrationCanceled(msg.sender);
        }
        else if(!Compare(AddPhone[msg.sender],str))
        {
            delete(AddPhone[msg.sender]);
            emit RegistrationCanceled(msg.sender);
        }

    }
    function GetOwner () public view returns(address)
    {
        return owner;
    }
    function SetOwner (address _owner) public
    {
        require(owner == msg.sender);
        owner = _owner;
    }
    function GetNumber() public view returns(string memory)
    {
        return(AddPhone[msg.sender]);
    }
    function PhoneValid(string memory _s) public pure returns (bool) {
        bytes memory byteString = bytes(_s);
        if (bytes(_s).length!=12||byteString[0]!="+")
        {
            return (false);
        }
        return (true);
    }

    function GetAddress(string memory _val) public view returns(address)
    {
        return (PhoneToAddress[_val]);
    }
    function ReturnAddList() public view returns(address,string memory)
    {
        return(Add_lists[NowAdd].add,Add_lists[NowAdd].phone);
    }
    function ConfirmedAdd(address _add) public {
        AddressToPhone[_add]=AddPhone[_add];
        PhoneToAddress[AddPhone[_add]]=_add;
        delete(AddPhone[_add]);
    }
    function NotConfirmed(address _add) public {
        delete(AddPhone[_add]);
        NowAdd=NowAdd+1;
    }

}


