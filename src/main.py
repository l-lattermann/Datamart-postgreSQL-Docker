from db import gen_seed_data as gen
from db import run_sql_files as setup


def main():
    """
    (1) Run all sql setup files.
    (2) Generate and fill all seed data.
    """
    # Run SQL files
    setup.run_sql_files()

    # Geneerate and fill all seed data
    gen.gen_dummydata_accounts()
    gen.gen_dummydata_credentials()
    gen.gen_dummydata_addresses()
    gen.gen_dummydata_accommodations()
    gen.gen_dummydata_images()
    gen.gen_dummydata_payment_methods()
    gen.gen_dummydata_credit_cards()
    gen.gen_dummydata_paypal()
    gen.gen_dummydata_reviews()
    gen.gen_dummydata_conversations()
    gen.gen_dummydata_messages()
    gen.gen_dummydata_review_images()
    gen.gen_dummydata_accommodation_images()
    gen.gen_dummydata_notifications()
    gen.gen_dummydata_payout_accounts()
    gen.gen_dummydata_bookings_and_payments()
    gen.gen_dummydata_payouts()
    gen.gen_dummydata_accommodation_calendar()
    gen.gen_dummydata_accommodation_amenities()


if __name__ == "__main__":
    main()