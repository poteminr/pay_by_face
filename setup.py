from argparse import ArgumentParser
import json
from blockchain import deploy_contract, get_owner_nonce , test_abi, get_owner, set_owner
from blockchain import get_private_key,private_key_to_address,check_number, check_pin
from config import set
from blockchain import check_accounts

parser = ArgumentParser(prog='Setup')

parser.add_argument('--deploy',
                    action='store_true',
                    help='Deploys registrar and certificates contracts to the blockchain')

parser.add_argument('--owner',
                    nargs=1,
                    metavar='contract',
                    type=str,
                    help='Prints user balance')
parser.add_argument('--chown',
                    nargs=2,
                    metavar='contract',
                    type=str,
                    help='change')

parser.add_argument('--add',
                    nargs=2,
                    metavar='contract',
                    type=str,
                    help='change')

args = parser.parse_args()

if args.deploy:
    nonce = get_owner_nonce()
    registrar = deploy_contract('registrar', nonce)
    print('KYC Registrar: %s' % registrar['address'])
    set('registrar.registrar', registrar)

    certificates = deploy_contract('certificates', nonce + 1)
    print('Payment Handler: %s' % certificates['address'])
    set('registrar.payments', certificates)

if args.owner:
    json_data = open('registrar.json').read()
    data = json.loads(json_data)
    contract_address = data['registrar']['address']
    owner = get_owner(test_abi, contract_address)
    print('Admin account:', owner)

if args.chown:
    priv_key_data = open('network.json').read()
    priv_key_opened = json.loads(priv_key_data)
    priv_key = priv_key_opened['privKey']

    json_data       = open('registrar.json').read()
    data = json.loads(json_data)
    contract_address = data['registrar']['address']

    private_key_address = private_key_to_address(priv_key)
    owner_address = get_owner(test_abi,contract_address)

    if private_key_address != owner_address:
        print('Request cannot be executed')
        pass

    else:
        set_owner(test_abi,contract_address,args.chown[1])
        print('New admin account:', get_owner(test_abi,contract_address))


if args.add:

    person_data = open('person.json').read()
    pers_data = json.loads(person_data)
    uuid= pers_data['id']
    pin = args.add[0]
    number = args.add[1]

    if not check_pin(uuid,pin):
        print('No funds to send the request')
        pass

    if not check_number(number):
        print('Incorrect phone number')
        pass


    try:
        json_data = open('person.json').read()
        data = json.loads(json_data)
        user_id = data['id']

    except Exception:
        print('ID is not found')
        pass

    try:
        json_data = open('registrar.json').read()
    except Exception:
        print('No contract address')
        pass
    try:
        json_data = open('registrar.json').read()
        data = json.loads(json_data)
        contract_address = data['registrar']['address']
        get_owner(test_abi,contract_address)
    except Exception:

        print('Seems that the contract address is not the registrar contract')

    private_key = get_private_key(uuid, pin)
    address = private_key_to_address(private_key)
    print('Registration request sent by', address)
    print(check_accounts(test_abi,contract_address))