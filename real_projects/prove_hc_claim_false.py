"""Proof that the hc-check claim is false. Copy into healthchecks/hc/api/tests/
and run: python manage.py test hc.api.tests.prove_hc_claim_false
Claim: period 1 h, grace 1 h, 'went down after only 70 minutes without a ping'."""
from datetime import timedelta as td
from django.utils.timezone import now
from hc.api.models import Check
from hc.test import BaseTestCase

class ProveHcClaimFalse(BaseTestCase):
    def test_not_down_at_70_minutes(self):
        c = Check.objects.create(project=self.project, kind="simple",
                                 timeout=td(hours=1), grace=td(hours=1), status="up",
                                 last_ping=now() - td(minutes=70))
        self.assertEqual(c.get_status(), "grace")            # late, not down
        self.assertEqual(c.going_down_after(), c.last_ping + td(hours=2))

    def test_down_only_after_two_hours(self):
        c = Check.objects.create(project=self.project, kind="simple",
                                 timeout=td(hours=1), grace=td(hours=1), status="up",
                                 last_ping=now() - td(minutes=119))
        self.assertEqual(c.get_status(), "grace")
        c.last_ping = now() - td(minutes=121)
        self.assertEqual(c.get_status(), "down")
