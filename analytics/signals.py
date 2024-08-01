from django.dispatch import Signal


object_view_signal = Signal(['sender', 'instance', 'request', 'user'])

